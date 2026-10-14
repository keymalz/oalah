import 'package:firebase_auth/firebase_auth.dart';

class AppUser {
  const AppUser({required this.uid, required this.name, required this.email, required this.provider});
  final String uid;
  final String name;
  final String email;
  final String provider;

  String get providerLabel => switch (provider) {
        'password' => 'Email dan password',
        'google.com' => 'Google',
        _ => provider,
      };
}

/// Kegagalan autentikasi dengan pesan Bahasa Indonesia yang siap ditampilkan.
class AuthFailure implements Exception {
  const AuthFailure(this.message, {this.cancelled = false});
  final String message;
  final bool cancelled;
  @override
  String toString() => message;
}

abstract class AuthRepository {
  Stream<AppUser?> get userChanges;
  Future<void> signInWithEmail(String email, String password);
  Future<void> register(String name, String email, String password);
  Future<void> signInWithGoogle();
  Future<void> signOut();
  Future<String?> idToken();
}

String friendlyAuthMessage(String code) {
  switch (code.replaceFirst('auth/', '')) {
    case 'invalid-email':
      return 'Format email tidak valid.';
    case 'user-not-found':
    case 'wrong-password':
    case 'invalid-credential':
      return 'Email atau password salah.';
    case 'email-already-in-use':
      return 'Email ini sudah terdaftar. Silakan masuk.';
    case 'weak-password':
      return 'Password terlalu lemah. Gunakan minimal 8 karakter.';
    case 'too-many-requests':
      return 'Terlalu banyak percobaan. Tunggu beberapa saat lalu coba lagi.';
    case 'network-request-failed':
      return 'Koneksi bermasalah. Periksa internet Anda.';
    case 'user-disabled':
      return 'Akun ini dinonaktifkan.';
    case 'popup-blocked':
      return 'Popup diblokir browser. Izinkan popup lalu coba lagi.';
    case 'account-exists-with-different-credential':
      return 'Email ini sudah terdaftar dengan metode login lain.';
    case 'operation-not-allowed':
      return 'Metode login ini belum diaktifkan di Firebase Console.';
    case 'unauthorized-domain':
      return 'Domain ini belum ada di Authorized domains Firebase.';
    default:
      return 'Terjadi kesalahan. Silakan coba lagi.';
  }
}

class FirebaseAuthRepository implements AuthRepository {
  FirebaseAuthRepository([FirebaseAuth? auth]) : _auth = auth ?? FirebaseAuth.instance;
  final FirebaseAuth _auth;

  AppUser? _map(User? u) => u == null
      ? null
      : AppUser(
          uid: u.uid,
          name: u.displayName ?? '',
          email: u.email ?? '',
          provider: u.providerData.isNotEmpty ? u.providerData.first.providerId : 'password',
        );

  @override
  Stream<AppUser?> get userChanges => _auth.userChanges().map(_map);

  Future<T> _guard<T>(Future<T> Function() body) async {
    try {
      return await body();
    } on FirebaseAuthException catch (e) {
      final cancelled = e.code == 'popup-closed-by-user' || e.code == 'cancelled-popup-request';
      throw AuthFailure(
        cancelled ? 'Login Google dibatalkan. Anda bisa mencoba lagi.' : friendlyAuthMessage(e.code),
        cancelled: cancelled,
      );
    }
  }

  @override
  Future<void> signInWithEmail(String email, String password) =>
      _guard(() => _auth.signInWithEmailAndPassword(email: email, password: password));

  @override
  Future<void> register(String name, String email, String password) => _guard(() async {
        final cred = await _auth.createUserWithEmailAndPassword(email: email, password: password);
        await cred.user?.updateDisplayName(name);
        await cred.user?.reload();
      });

  @override
  Future<void> signInWithGoogle() => _guard(() => _auth.signInWithPopup(GoogleAuthProvider()));

  @override
  Future<void> signOut() => _auth.signOut();

  @override
  Future<String?> idToken() async => _auth.currentUser?.getIdToken();
}
