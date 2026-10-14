import 'dart:async';
import 'dart:convert';

import 'package:auth_gemini_web/app.dart';
import 'package:auth_gemini_web/services/auth_repository.dart';
import 'package:auth_gemini_web/services/gemini_client.dart';
import 'package:auth_gemini_web/validators.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

class FakeAuth implements AuthRepository {
  final _c = StreamController<AppUser?>.broadcast();
  AppUser? _u;
  bool googleCancel = false;
  @override
  Stream<AppUser?> get userChanges async* {
    yield _u;
    yield* _c.stream;
  }

  void _set(AppUser? u) {
    _u = u;
    _c.add(u);
  }

  @override
  Future<void> signInWithEmail(String email, String password) async {
    if (password != 'Rahasia123') throw const AuthFailure('Email atau password salah.');
    _set(AppUser(uid: '1', name: 'Uji', email: email, provider: 'password'));
  }

  @override
  Future<void> register(String name, String email, String password) async =>
      _set(AppUser(uid: '2', name: name, email: email, provider: 'password'));

  @override
  Future<void> signInWithGoogle() async {
    if (googleCancel) throw const AuthFailure('Login Google dibatalkan. Anda bisa mencoba lagi.', cancelled: true);
    _set(const AppUser(uid: '3', name: 'G User', email: 'g@example.com', provider: 'google.com'));
  }

  @override
  Future<void> signOut() async => _set(null);
  @override
  Future<String?> idToken() async => _u == null ? null : 'token-palsu';
}

Widget build(FakeAuth auth, http.Client client) =>
    AuthGeminiApp(auth: auth, gemini: GeminiClient(auth, client: client, baseUrl: 'http://api.test'));

void main() {
  test('validator', () {
    expect(validateEmail('abc'), isNotNull);
    expect(validateEmail('a@b.co'), isNull);
    expect(validateNewPassword('abcdefgh'), isNotNull);
    expect(validateNewPassword('abcdefg1'), isNull);
    expect(validateConfirm('x', 'y'), 'Konfirmasi password tidak cocok.');
  });

  testWidgets('login: validasi, kredensial salah, sukses, logout', (t) async {
    final auth = FakeAuth();
    await t.pumpWidget(build(auth, MockClient((_) async => http.Response('{}', 200))));
    await t.pumpAndSettle();

    await t.tap(find.byKey(const Key('login-submit')));
    await t.pump();
    expect(find.text('Email wajib diisi.'), findsOneWidget);
    expect(find.text('Password wajib diisi.'), findsOneWidget);

    await t.enterText(find.byKey(const Key('login-email')), 'bukan-email');
    await t.tap(find.byKey(const Key('login-submit')));
    await t.pump();
    expect(find.text('Format email tidak valid.'), findsOneWidget);

    await t.enterText(find.byKey(const Key('login-email')), 'uji@example.com');
    await t.enterText(find.byKey(const Key('login-password')), 'salah');
    await t.tap(find.byKey(const Key('login-submit')));
    await t.pumpAndSettle();
    expect(find.text('Email atau password salah.'), findsOneWidget);

    await t.enterText(find.byKey(const Key('login-password')), 'Rahasia123');
    await t.tap(find.byKey(const Key('login-submit')));
    await t.pumpAndSettle();
    expect(find.text('Halo, Uji'), findsOneWidget);
    expect(find.text('Email dan password'), findsOneWidget);

    await t.tap(find.byKey(const Key('logout')));
    await t.pumpAndSettle();
    expect(find.text('Masuk'), findsWidgets);
    expect(find.byKey(const Key('login-submit')), findsOneWidget);
  });

  testWidgets('register: konfirmasi password tidak cocok', (t) async {
    final auth = FakeAuth();
    await t.pumpWidget(build(auth, MockClient((_) async => http.Response('{}', 200))));
    await t.pumpAndSettle();
    await t.tap(find.text('Daftar di sini'));
    await t.pumpAndSettle();
    await t.enterText(find.byKey(const Key('reg-name')), 'Budi');
    await t.enterText(find.byKey(const Key('reg-email')), 'budi@example.com');
    await t.enterText(find.byKey(const Key('reg-password')), 'Rahasia123');
    await t.enterText(find.byKey(const Key('reg-confirm')), 'Beda12345');
    await t.ensureVisible(find.byKey(const Key('reg-submit')));
    await t.tap(find.byKey(const Key('reg-submit')));
    await t.pump();
    expect(find.text('Konfirmasi password tidak cocok.'), findsOneWidget);
  });

  testWidgets('login Google dibatalkan menampilkan pesan, lalu sukses', (t) async {
    final auth = FakeAuth()..googleCancel = true;
    await t.pumpWidget(build(auth, MockClient((_) async => http.Response('{}', 200))));
    await t.pumpAndSettle();
    await t.tap(find.text('Masuk dengan Google'));
    await t.pumpAndSettle();
    expect(find.textContaining('dibatalkan'), findsOneWidget);
    auth.googleCancel = false;
    await t.tap(find.text('Masuk dengan Google'));
    await t.pumpAndSettle();
    expect(find.text('Google'), findsOneWidget);
  });

  testWidgets('Tanya Gemini: kirim Bearer token, tampilkan jawaban & tangani 401', (t) async {
    final auth = FakeAuth();
    String? seenAuth;
    var status = 200;
    final client = MockClient((req) async {
      seenAuth = req.headers['Authorization'];
      expect(req.url.toString(), 'http://api.test/api/gemini');
      return status == 200
          ? http.Response(jsonEncode({'answer': 'Halo dari Gemini', 'model': 'fake', 'mock': false}), 200)
          : http.Response(jsonEncode({'error': 'Sesi berakhir', 'code': 'SESSION_EXPIRED'}), 401);
    });
    await t.pumpWidget(build(auth, client));
    await t.pumpAndSettle();
    await auth.signInWithEmail('uji@example.com', 'Rahasia123');
    await t.pumpAndSettle();

    await t.enterText(find.byKey(const Key('prompt')), 'Halo');
    await t.tap(find.byKey(const Key('ask')));
    await t.pumpAndSettle();
    expect(seenAuth, 'Bearer token-palsu');
    expect(find.text('Halo dari Gemini'), findsOneWidget);

    status = 401;
    await t.tap(find.byKey(const Key('ask')));
    await t.pumpAndSettle();
    expect(find.text('Sesi Anda sudah berakhir. Silakan masuk lagi.'), findsOneWidget);
    expect(find.byKey(const Key('login-submit')), findsOneWidget);
  });
}
