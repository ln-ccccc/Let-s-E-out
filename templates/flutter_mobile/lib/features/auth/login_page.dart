import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';
import '../../shared/auth/auth_store.dart';
import '../home/home_page.dart';
import 'otp_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.api, required this.authStore});

  final ApiClient api;
  final AuthStore authStore;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController _phone = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    _phone.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    final phone = _phone.text.trim();
    if (phone.isEmpty) return;
    setState(() => _loading = true);
    try {
      await widget.api.requestOtp(phone);
      if (!mounted) return;
      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => OtpPage(
            api: widget.api,
            authStore: widget.authStore,
            phone: phone,
          ),
        ),
      );
      final token = await widget.authStore.getToken();
      if (!mounted) return;
      if (token != null && token.isNotEmpty) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => HomePage(api: widget.api, authStore: widget.authStore),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('登录')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('手机号验证码（开发环境验证码固定为 000000）'),
            const SizedBox(height: 12),
            TextField(
              controller: _phone,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(labelText: '手机号'),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: _loading ? null : _requestOtp,
              child: _loading ? const CircularProgressIndicator() : const Text('获取验证码'),
            ),
          ],
        ),
      ),
    );
  }
}

