import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';

class CreateVisitPage extends StatefulWidget {
  const CreateVisitPage({super.key, required this.api});

  final ApiClient api;

  @override
  State<CreateVisitPage> createState() => _CreateVisitPageState();
}

class _CreateVisitPageState extends State<CreateVisitPage> {
  final TextEditingController _placeName = TextEditingController();
  final TextEditingController _city = TextEditingController(text: '武汉');
  final TextEditingController _area = TextEditingController();
  final TextEditingController _highlights = TextEditingController();
  final TextEditingController _pitfalls = TextEditingController();

  String _dayPart = 'dinner';
  String _revisitIntent = 'maybe';
  bool _public = false;
  bool _loading = false;

  @override
  void dispose() {
    _placeName.dispose();
    _city.dispose();
    _area.dispose();
    _highlights.dispose();
    _pitfalls.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final name = _placeName.text.trim();
    final city = _city.text.trim();
    final highlights = _highlights.text.trim();
    final pitfalls = _pitfalls.text.trim();
    if (name.isEmpty || city.isEmpty || highlights.isEmpty || pitfalls.isEmpty) return;

    setState(() => _loading = true);
    try {
      final place = await widget.api.createPlace(
        name: name,
        city: city,
        area: _area.text.trim().isEmpty ? null : _area.text.trim(),
      );
      final placeId = place['id']?.toString() ?? '';
      await widget.api.createVisit(
        placeId: placeId,
        dayPart: _dayPart,
        highlights: highlights,
        pitfalls: pitfalls,
        revisitIntent: _revisitIntent,
        publishStatus: _public ? 'public' : 'private',
      );
      if (!mounted) return;
      Navigator.of(context).pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('新建复盘')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(controller: _placeName, decoration: const InputDecoration(labelText: '店名*')),
          const SizedBox(height: 12),
          TextField(controller: _city, decoration: const InputDecoration(labelText: '城市*')),
          const SizedBox(height: 12),
          TextField(controller: _area, decoration: const InputDecoration(labelText: '区域/商圈')),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _dayPart,
            items: const [
              DropdownMenuItem(value: 'breakfast', child: Text('早餐')),
              DropdownMenuItem(value: 'lunch', child: Text('午餐')),
              DropdownMenuItem(value: 'dinner', child: Text('晚餐')),
              DropdownMenuItem(value: 'late_night', child: Text('夜宵')),
              DropdownMenuItem(value: 'other', child: Text('其他')),
            ],
            onChanged: (v) => setState(() => _dayPart = v ?? _dayPart),
            decoration: const InputDecoration(labelText: '时段*'),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _revisitIntent,
            items: const [
              DropdownMenuItem(value: 'yes', child: Text('会')),
              DropdownMenuItem(value: 'maybe', child: Text('看情况')),
              DropdownMenuItem(value: 'no', child: Text('不会')),
            ],
            onChanged: (v) => setState(() => _revisitIntent = v ?? _revisitIntent),
            decoration: const InputDecoration(labelText: '会不会再去*'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _highlights,
            decoration: const InputDecoration(labelText: '推荐点*'),
            minLines: 2,
            maxLines: 4,
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _pitfalls,
            decoration: const InputDecoration(labelText: '踩坑点*'),
            minLines: 2,
            maxLines: 4,
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            value: _public,
            onChanged: (v) => setState(() => _public = v),
            title: const Text('公开发布'),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: _loading ? null : _submit,
            child: _loading ? const CircularProgressIndicator() : const Text('保存'),
          ),
        ],
      ),
    );
  }
}

