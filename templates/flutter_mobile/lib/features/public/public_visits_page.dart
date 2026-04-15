import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';

class PublicVisitsPage extends StatefulWidget {
  const PublicVisitsPage({super.key, required this.api});

  final ApiClient api;

  @override
  State<PublicVisitsPage> createState() => _PublicVisitsPageState();
}

class _PublicVisitsPageState extends State<PublicVisitsPage> {
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.listPublicVisits();
  }

  void _refresh() {
    setState(() {
      _future = widget.api.listPublicVisits();
    });
  }

  Future<void> _refreshAsync() async {
    _refresh();
    await _future;
  }

  Future<void> _favorite(String id) async {
    try {
      await widget.api.favorite(id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('已收藏')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  Future<void> _report(String id) async {
    try {
      await widget.api.reportVisit(id, 'other');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('已举报')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Text(snapshot.error.toString()));
        }
        final items = snapshot.data ?? [];
        if (items.isEmpty) {
          return RefreshIndicator(
            onRefresh: _refreshAsync,
            child: ListView(
              children: const [
                SizedBox(height: 120),
                Center(child: Text('还没有公开内容')),
              ],
            ),
          );
        }
        return RefreshIndicator(
          onRefresh: _refreshAsync,
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemBuilder: (context, i) {
              final v = items[i];
              final id = v['id']?.toString() ?? '';
              final place = v['place'] as Map<String, dynamic>? ?? {};
              final title = place['name']?.toString() ?? '';
              final subtitle = v['highlights']?.toString() ?? '';
              return ListTile(
                title: Text(title),
                subtitle: Text(subtitle, maxLines: 2, overflow: TextOverflow.ellipsis),
                trailing: PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'fav') _favorite(id);
                    if (value == 'report') _report(id);
                  },
                  itemBuilder: (_) => const [
                    PopupMenuItem(value: 'fav', child: Text('收藏')),
                    PopupMenuItem(value: 'report', child: Text('举报')),
                  ],
                ),
              );
            },
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemCount: items.length,
          ),
        );
      },
    );
  }
}

