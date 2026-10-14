import 'package:flutter/material.dart';

import '../config.dart';
import '../services/auth_repository.dart';
import '../services/gemini_client.dart';
import '../widgets.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key, required this.user, required this.auth, required this.gemini, required this.onSessionExpired});
  final AppUser user;
  final AuthRepository auth;
  final GeminiClient gemini;
  final VoidCallback onSessionExpired;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final _prompt = TextEditingController();
  bool _busy = false;
  String? _error;
  String _answer = 'Jawaban akan muncul di sini.';
  String _meta = '';

  @override
  void dispose() {
    _prompt.dispose();
    super.dispose();
  }

  Future<void> _ask() async {
    if (_busy) return;
    final text = _prompt.text.trim();
    if (text.isEmpty) {
      setState(() => _error = 'Pertanyaan tidak boleh kosong.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _answer = 'Gemini sedang menjawab…';
      _meta = '';
    });
    try {
      final r = await widget.gemini.ask(text);
      if (!mounted) return;
      setState(() {
        _answer = r.text;
        _meta = r.mock ? 'MOCK — bukan jawaban Gemini asli (mode pengujian).' : 'Model: ${r.model}';
      });
    } on GeminiException catch (e) {
      if (!mounted) return;
      if (e.unauthorized) {
        widget.onSessionExpired();
        return;
      }
      setState(() {
        _answer = 'Tidak ada jawaban.';
        _error = e.message;
      });
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final u = widget.user;
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Praktikum Auth & Gemini · Flutter Web'),
        actions: [
          TextButton.icon(
            key: const Key('logout'),
            onPressed: widget.auth.signOut,
            icon: const Icon(Icons.logout),
            label: const Text('Keluar'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 760),
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('Halo, ${u.name.isNotEmpty ? u.name : u.email}', style: theme.textTheme.headlineSmall),
                    const SizedBox(height: 12),
                    _row('Nama', u.name.isEmpty ? '(belum diisi)' : u.name),
                    _row('Email', u.email),
                    _row('Metode login', u.providerLabel),
                  ]),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                    Text('Tanya Gemini', style: theme.textTheme.titleLarge),
                    const SizedBox(height: 12),
                    MessageBanner(message: _error),
                    TextField(
                      key: const Key('prompt'),
                      controller: _prompt,
                      maxLines: 4,
                      maxLength: AppConfig.maxPromptChars,
                      decoration: const InputDecoration(
                        labelText: 'Pertanyaan Anda',
                        hintText: 'Contoh: Jelaskan apa itu Firebase Authentication dalam 3 kalimat.',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    FilledButton(
                      key: const Key('ask'),
                      onPressed: _busy ? null : _ask,
                      style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
                      child: Text(_busy ? 'Menunggu Gemini…' : 'Kirim ke Gemini'),
                    ),
                    const SizedBox(height: 16),
                    Text('Jawaban', style: theme.textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Container(
                      key: const Key('answer'),
                      padding: const EdgeInsets.all(12),
                      constraints: const BoxConstraints(minHeight: 64),
                      decoration: BoxDecoration(
                        border: Border.all(color: theme.colorScheme.outlineVariant),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: SelectableText(_answer),
                    ),
                    if (_meta.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text(_meta, style: theme.textTheme.bodySmall)),
                  ]),
                ),
              ),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _row(String k, String v) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          SizedBox(width: 120, child: Text(k, style: TextStyle(color: Theme.of(context).colorScheme.outline))),
          Expanded(child: SelectableText(v, style: const TextStyle(fontWeight: FontWeight.w600))),
        ]),
      );
}
