/// Konfigurasi diberikan lewat `--dart-define` saat run/build.
/// Tidak ada rahasia di sini: nilai Firebase web bersifat publik, dan API key
/// Gemini TIDAK PERNAH ada di aplikasi Flutter (hanya di server Node.js).
class AppConfig {
  static const apiBaseUrl =
      String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:3000');

  static const useAuthEmulator = bool.fromEnvironment('USE_AUTH_EMULATOR');
  static const authEmulatorHost =
      String.fromEnvironment('AUTH_EMULATOR_HOST', defaultValue: '127.0.0.1');
  static const authEmulatorPort =
      int.fromEnvironment('AUTH_EMULATOR_PORT', defaultValue: 9099);

  static const maxPromptChars = 2000;
}
