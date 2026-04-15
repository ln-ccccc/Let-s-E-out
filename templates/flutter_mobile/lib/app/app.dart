import 'package:flutter/material.dart';

import '../features/auth/login_page.dart';
import '../features/home/home_page.dart';
import '../shared/api/api_client.dart';
import '../shared/auth/auth_store.dart';

class App extends StatefulWidget {
  const App({super.key});

  @override
  State<App> createState() => _AppState();
}

class _AppState extends State<App> {
  late final AuthStore _authStore;
  late final ApiClient _api;

  @override
  void initState() {
    super.initState();
    _authStore = AuthStore();
    _api = ApiClient(authStore: _authStore);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '探店复盘',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.teal),
      home: FutureBuilder<String?>(
        future: _authStore.getToken(),
        builder: (context, snapshot) {
          final token = snapshot.data;
          if (snapshot.connectionState != ConnectionState.done) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
          if (token == null || token.isEmpty) {
            return LoginPage(api: _api, authStore: _authStore);
          }
          return HomePage(api: _api, authStore: _authStore);
        },
      ),
    );
  }
}
