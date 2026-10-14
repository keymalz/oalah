import 'package:firebase_core/firebase_core.dart';

/// Pengganti `firebase_options.dart` hasil `flutterfire configure`.
/// Nilai diisi lewat `--dart-define` (lihat README). Untuk alur resmi FlutterFire CLI,
/// file ini dapat ditimpa oleh hasil `flutterfire configure`.
class DefaultFirebaseOptions {
  static const currentPlatform = FirebaseOptions(
    apiKey: String.fromEnvironment('FIREBASE_API_KEY', defaultValue: 'demo-api-key'),
    appId: String.fromEnvironment('FIREBASE_APP_ID', defaultValue: '1:000000000000:web:demo'),
    messagingSenderId:
        String.fromEnvironment('FIREBASE_MESSAGING_SENDER_ID', defaultValue: '000000000000'),
    projectId:
        String.fromEnvironment('FIREBASE_PROJECT_ID', defaultValue: 'demo-auth-gemini'),
    authDomain: String.fromEnvironment('FIREBASE_AUTH_DOMAIN', defaultValue: ''),
  );
}
