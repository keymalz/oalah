import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'app.dart';
import 'config.dart';
import 'firebase_options.dart';
import 'services/auth_repository.dart';
import 'services/gemini_client.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  if (AppConfig.useAuthEmulator) {
    // Hanya untuk pengujian lokal (flag --dart-define=USE_AUTH_EMULATOR=true).
    await FirebaseAuth.instance.useAuthEmulator(AppConfig.authEmulatorHost, AppConfig.authEmulatorPort);
  }
  final auth = FirebaseAuthRepository();
  runApp(AuthGeminiApp(auth: auth, gemini: GeminiClient(auth)));
}
