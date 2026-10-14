import 'package:flutter/material.dart';

import 'pages/dashboard_page.dart';
import 'pages/login_page.dart';
import 'services/auth_repository.dart';
import 'services/gemini_client.dart';

class AuthGeminiApp extends StatelessWidget {
  const AuthGeminiApp({super.key, required this.auth, required this.gemini});
  final AuthRepository auth;
  final GeminiClient gemini;

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Praktikum Auth & Gemini',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: const Color(0xFF3949AB), useMaterial3: true),
        darkTheme: ThemeData(colorSchemeSeed: const Color(0xFF3949AB), brightness: Brightness.dark, useMaterial3: true),
        // Semua URL melewati AuthGate: halaman dashboard tidak bisa dibuka tanpa login.
        onGenerateRoute: (_) => MaterialPageRoute(builder: (_) => AuthGate(auth: auth, gemini: gemini)),
      );
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key, required this.auth, required this.gemini});
  final AuthRepository auth;
  final GeminiClient gemini;

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  String? _notice;

  Future<void> _expired() async {
    await widget.auth.signOut();
    if (mounted) setState(() => _notice = 'Sesi Anda sudah berakhir. Silakan masuk lagi.');
  }

  @override
  Widget build(BuildContext context) => StreamBuilder<AppUser?>(
        stream: widget.auth.userChanges,
        builder: (context, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Scaffold(body: Center(child: CircularProgressIndicator()));
          }
          final user = snap.data;
          if (user == null) {
            // Navigator sendiri untuk perpindahan login <-> register.
            return Navigator(
              onGenerateRoute: (_) => MaterialPageRoute(builder: (_) => LoginPage(auth: widget.auth, notice: _notice)),
            );
          }
          _notice = null;
          return DashboardPage(user: user, auth: widget.auth, gemini: widget.gemini, onSessionExpired: _expired);
        },
      );
}
