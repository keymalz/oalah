final _emailRe = RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$');

String? validateName(String? v) {
  final s = (v ?? '').trim();
  if (s.length < 2) return 'Nama minimal 2 karakter.';
  if (s.length > 60) return 'Nama maksimal 60 karakter.';
  return null;
}

String? validateEmail(String? v) {
  final s = (v ?? '').trim();
  if (s.isEmpty) return 'Email wajib diisi.';
  if (!_emailRe.hasMatch(s)) return 'Format email tidak valid.';
  return null;
}

String? validateLoginPassword(String? v) => (v ?? '').isEmpty ? 'Password wajib diisi.' : null;

String? validateNewPassword(String? v) {
  final s = v ?? '';
  if (s.length < 8) return 'Password minimal 8 karakter.';
  if (!RegExp(r'[A-Za-z]').hasMatch(s) || !RegExp(r'\d').hasMatch(s)) {
    return 'Password harus mengandung huruf dan angka.';
  }
  return null;
}

String? validateConfirm(String? v, String password) {
  if ((v ?? '').isEmpty) return 'Konfirmasi password wajib diisi.';
  if (v != password) return 'Konfirmasi password tidak cocok.';
  return null;
}
