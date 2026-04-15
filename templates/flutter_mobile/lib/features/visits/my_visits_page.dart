import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';
import 'create_visit_page.dart';

class MyVisitsPage extends StatefulWidget {
  const MyVisitsPage({super.key, required this.api});

  final ApiClient api;

  @override
  State<MyVisitsPage> createState() => _MyVisitsPageState();
}

class _MyVisitsPageState extends State<MyVisitsPage> {
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.listMyVisits();
  }

  void _refresh() {
    setState(() {
      _future = widget.api.listMyVisits();
    });
  }

  Future<void> _refreshAsync() async {
    _refresh();
    await _future;
  }

  Future<void> _openCreate() async {
    await Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => CreateVisitPage(api: widget.api)),
    );
    _refresh();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: _openCreate,
        child: const Icon(Icons.add),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
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
            return const Center(child: Text('还没有复盘，先记一条吧'));
          }
          return RefreshIndicator(
            onRefresh: _refreshAsync,
            child: ListView.separated(
              padding: const EdgeInsets.all(12),
              itemBuilder: (context, i) {
                final v = items[i];
                final place = v['place'] as Map<String, dynamic>? ?? {};
                final title = place['name']?.toString() ?? '';
                final area = place['area']?.toString();
                final subtitle = v['highlights']?.toString() ?? '';
                final status = v['publishStatus']?.toString() ?? '';
                return ListTile(
                  title: Text(area == null || area.isEmpty ? title : '$title · $area'),
                  subtitle: Text(subtitle, maxLines: 2, overflow: TextOverflow.ellipsis),
                  trailing: Text(status),
                );
              },
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemCount: items.length,
            ),
          );
        },
      ),
    );
  }
}
