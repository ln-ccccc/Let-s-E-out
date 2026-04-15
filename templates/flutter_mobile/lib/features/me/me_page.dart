import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';

class MePage extends StatefulWidget {
  const MePage({super.key, required this.api});

  final ApiClient api;

  @override
  State<MePage> createState() => _MePageState();
}

class _MePageState extends State<MePage> {
  late Future<Map<String, dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.getMe();
  }

  void _refresh() {
    setState(() {
      _future = widget.api.getMe();
    });
  }

  Future<void> _openFeedback() async {
    final controller = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) {
        bool submitting = false;
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('反馈与建议'),
              content: TextField(
                controller: controller,
                minLines: 3,
                maxLines: 6,
                decoration: const InputDecoration(hintText: '写点什么...'),
              ),
              actions: [
                TextButton(
                  onPressed: submitting ? null : () => Navigator.of(context).pop(false),
                  child: const Text('取消'),
                ),
                FilledButton(
                  onPressed: submitting
                      ? null
                      : () async {
                          final msg = controller.text.trim();
                          if (msg.isEmpty) return;
                          setState(() => submitting = true);
                          try {
                            await widget.api.submitFeedback('suggestion', msg);
                            if (!context.mounted) return;
                            Navigator.of(context).pop(true);
                          } catch (e) {
                            if (!context.mounted) return;
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(e.toString())),
                            );
                            setState(() => submitting = false);
                          }
                        },
                  child: submitting ? const CircularProgressIndicator() : const Text('提交'),
                ),
              ],
            );
          },
        );
      },
    );
    controller.dispose();
    if (!mounted) return;
    if (ok == true) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('已提交')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Text(snapshot.error.toString()));
        }
        final me = snapshot.data ?? {};
        final nickname = me['nickname']?.toString() ?? '';
        final role = me['role']?.toString() ?? '';
        return ListView(
          children: [
            ListTile(title: Text(nickname), subtitle: Text(role)),
            ListTile(
              title: const Text('反馈与建议'),
              trailing: const Icon(Icons.chevron_right),
              onTap: _openFeedback,
            ),
            ListTile(
              title: const Text('刷新资料'),
              trailing: const Icon(Icons.refresh),
              onTap: _refresh,
            ),
          ],
        );
      },
    );
  }
}

