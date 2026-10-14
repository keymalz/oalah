import 'package:flutter/material.dart';

import '../services/auth_repository.dart';
import '../validators.dart';
import '../widgets.dart';
import 'login_page.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key, required this.auth});
  final AuthRepository auth;

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _form = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return;
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
    _run(() => widget.auth.register(_name.text.trim(), _email.text.trim(), _password.text));
  }

  @override
  Widget build(BuildContext context) => AuthCard(
        child: Form(
          key: _form,
          child: AutofillGroup(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Daftar akun', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 4),
                const Text('Buat akun baru dengan email dan password, atau gunakan akun Google.'),
                const SizedBox(height: 16),
                MessageBanner(message: _error),
                TextFormField(
                  key: const Key('reg-name'),
                  controller: _name,
                  autofillHints: const [AutofillHints.name],
                  textInputAction: TextInputAction.next,
                  validator: validateName,
                  decoration: const InputDecoration(labelText: 'Nama', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  key: const Key('reg-email'),
                  controller: _email,
                  keyboardType: TextInputType.emailAddress,
                  autofillHints: const [AutofillHints.email],
                  textInputAction: TextInputAction.next,
                  validator: validateEmail,
                  decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 16),
                PasswordField(
                  key: const Key('reg-password'),
                  controller: _password,
                  label: 'Password (min. 8 karakter, huruf dan angka)',
                  validator: validateNewPassword,
                  autofillHints: const [AutofillHints.newPassword],
                  textInputAction: TextInputAction.next,
                ),
                const SizedBox(height: 16),
                PasswordField(
                  key: const Key('reg-confirm'),
                  controller: _confirm,
                  label: 'Konfirmasi password',
                  validator: (v) => validateConfirm(v, _password.text),
                  textInputAction: TextInputAction.done,
                  onSubmitted: _submit,
                ),
                const SizedBox(height: 20),
                FilledButton(
                  key: const Key('reg-submit'),
                  onPressed: _busy ? null : _submit,
                  style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
                  child: _busy
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Daftar'),
                ),
                const SizedBox(height: 16),
                const Row(children: [Expanded(child: Divider()), Padding(padding: EdgeInsets.all(8), child: Text('atau')), Expanded(child: Divider())]),
                const SizedBox(height: 8),
                GoogleButton(
                  label: 'Daftar dengan Google',
                  onPressed: _busy ? null : () => _run(widget.auth.signInWithGoogle),
                ),
                const SizedBox(height: 16),
                Wrap(alignment: WrapAlignment.center, crossAxisAlignment: WrapCrossAlignment.center, children: [
                  const Text('Sudah punya akun?'),
                  TextButton(
                    onPressed: _busy
                        ? null
                        : () => Navigator.of(context).pushReplacement(
                            MaterialPageRoute(builder: (_) => LoginPage(auth: widget.auth))),
                    child: const Text('Masuk'),
                  ),
                ]),
              ],
            ),
          ),
        ),
      );
}
