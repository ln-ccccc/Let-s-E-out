import 'package:flutter/material.dart';

import '../../shared/api/api_client.dart';
import '../../shared/auth/auth_store.dart';
import '../auth/login_page.dart';
import '../favorites/favorites_page.dart';
import '../me/me_page.dart';
import '../public/public_visits_page.dart';
import '../visits/my_visits_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.api, required this.authStore});

  final ApiClient api;
  final AuthStore authStore;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _index = 0;

  Future<void> _logout() async {
    await widget.authStore.clear();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => LoginPage(api: widget.api, authStore: widget.authStore)),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      MyVisitsPage(api: widget.api),
      PublicVisitsPage(api: widget.api),
      FavoritesPage(api: widget.api),
      MePage(api: widget.api),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('探店复盘'),
        actions: [
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        backgroundColor: Colors.white,
        elevation: 0,
        indicatorColor: const Color(0xFF2C3E50).withOpacity(0.1),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined), 
            selectedIcon: Icon(Icons.receipt_long, color: Color(0xFF2C3E50)),
            label: '我的'
          ),
          NavigationDestination(
            icon: Icon(Icons.public_outlined), 
            selectedIcon: Icon(Icons.public, color: Color(0xFF2C3E50)),
            label: '公开'
          ),
          NavigationDestination(
            icon: Icon(Icons.bookmark_outline), 
            selectedIcon: Icon(Icons.bookmark, color: Color(0xFF2C3E50)),
            label: '收藏'
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline), 
            selectedIcon: Icon(Icons.person, color: Color(0xFF2C3E50)),
            label: '我的页'
          ),
        ],
      ),
    );
  }
}

