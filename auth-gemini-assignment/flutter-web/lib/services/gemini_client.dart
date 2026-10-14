import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config.dart';
import 'auth_repository.dart';

class GeminiAnswer {
  const GeminiAnswer(this.text, this.model, this.mock);
  final String text;
  final String model;
  final bool mock;
}

class GeminiException implements Exception {
  const GeminiException(this.message, {this.unauthorized = false});
  final String message;
  final bool unauthorized;
  @override
  String toString() => message;
}

/// Memanggil backend Node.js. Browser mengirim Firebase ID token sebagai Bearer;
/// server memverifikasinya sebelum meneruskan ke Gemini.
class GeminiClient {
  GeminiClient(this._auth, {http.Client? client, String? baseUrl})
      : _http = client ?? http.Client(),
        _base = baseUrl ?? AppConfig.apiBaseUrl;

  final AuthRepository _auth;
  final http.Client _http;
  final String _base;

  Future<GeminiAnswer> ask(String prompt) async {
    final token = await _auth.idToken();
    if (token == null) throw const GeminiException('Anda belum masuk.', unauthorized: true);
    final http.Response res;
    try {
      res = await _http
          .post(
            Uri.parse('$_base/api/gemini'),
            headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
            body: jsonEncode({'prompt': prompt}),
          )
          .timeout(const Duration(seconds: 30));
    } on TimeoutException {
      throw const GeminiException('Server tidak merespons tepat waktu.');
    } catch (_) {
      throw const GeminiException('Tidak dapat terhubung ke server backend. Pastikan server Node.js berjalan.');
    }
    Map<String, dynamic> body = {};
    try {
      body = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    } catch (_) {}
    if (res.statusCode == 200) {
      return GeminiAnswer(body['answer'] as String? ?? '', body['model'] as String? ?? '', body['mock'] == true);
    }
    if (res.statusCode == 401) {
      throw GeminiException(body['error'] as String? ?? 'Sesi berakhir. Silakan masuk lagi.', unauthorized: true);
    }
    throw GeminiException(body['error'] as String? ?? 'Gagal menghubungi Gemini (${res.statusCode}).');
  }
}
