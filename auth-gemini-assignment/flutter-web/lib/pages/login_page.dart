import 'package:flutter/material.dart';

import '../services/auth_repository.dart';
import '../validators.dart';
import '../widgets.dart';
import 'register_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.auth, this.notice});
  final AuthRepository auth;
  final String? notice;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return; // cegah submit berulang
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await action();
    } on AuthFailure catch (e) {
      if (mounted) setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _submit() {
    if (!(_form.currentState?.validate() ?? false)) return;
    _run(() => widget.auth.signInWithEmail(_email.text.trim(), _password.text));
  }

  @override
  Widget build(BuildContext context) => AuthCard(
        child: Form(
          key: _form,
          child: AutofillGroup(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Masuk', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 4),
                const Text('Masuk untuk membuka dashboard dan fitur Tanya Gemini.'),
                const SizedBox(height: 16),
                MessageBanner(message: _error ?? widget.notice),
                TextFormField(
                  key: const Key('login-email'),
                  controller: _email,
                  keyboardType: TextInputType.emailAddress,
                  autofillHints: const [AutofillHints.email],
                  textInputAction: TextInputAction.next,
                  validator: validateEmail,
                  decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 16),
                PasswordField(
                  key: const Key('login-password'),
                  controller: _password,
                  label: 'Password',
                  validator: validateLoginPassword,
                  autofillHints: const [AutofillHints.password],
                  textInputAction: TextInputAction.done,
                  onSubmitted: _submit,
                ),
                const SizedBox(height: 20),
                FilledButton(
                  key: const Key('login-submit'),
                  onPressed: _busy ? null : _submit,
                  style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
                  child: _busy
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Masuk'),
                ),
                const SizedBox(height: 16),
                const Row(children: [Expanded(child: Divider()), Padding(padding: EdgeInsets.all(8), child: Text('atau')), Expanded(child: Divider())]),
                const SizedBox(height: 8),
                GoogleButton(
                  label: 'Masuk dengan Google',
                  onPressed: _busy ? null : () => _run(widget.auth.signInWithGoogle),
                ),
                const SizedBox(height: 16),
                Wrap(alignment: WrapAlignment.center, crossAxisAlignment: WrapCrossAlignment.center, children: [
                  const Text('Belum punya akun?'),
                  TextButton(
                    onPressed: _busy
                        ? null
                        : () => Navigator.of(context).pushReplacement(
                            MaterialPageRoute(builder: (_) => RegisterPage(auth: widget.auth))),
                    child: const Text('Daftar di sini'),
                  ),
                ]),
              ],
            ),
          ),
        ),
      );
}
