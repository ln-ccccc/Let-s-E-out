import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';

class FavoritesPage extends StatefulWidget {
  const FavoritesPage({super.key, required this.api});

  final ApiClient api;

  @override
  State<FavoritesPage> createState() => _FavoritesPageState();
}

class _FavoritesPageState extends State<FavoritesPage> {
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.listFavorites();
  }

  void _refresh() {
    setState(() {
      _future = widget.api.listFavorites();
    });
  }

  Future<void> _refreshAsync() async {
    _refresh();
    await _future;
  }

  Future<void> _unfavorite(String id) async {
    try {
      await widget.api.unfavorite(id);
      _refresh();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('已取消收藏')));
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
                Center(child: Text('还没有收藏')),
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
                trailing: IconButton(
                  onPressed: () => _unfavorite(id),
                  icon: const Icon(Icons.bookmark_remove),
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

