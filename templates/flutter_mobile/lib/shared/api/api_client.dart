import 'dart:convert';

import 'package:http/http.dart' as http;

import '../auth/auth_store.dart';

class ApiClient {
  ApiClient({required this.authStore});

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  final AuthStore authStore;
  final http.Client _client = http.Client();

  Future<Map<String, dynamic>> _request(
    String method,
    String path, {
    Map<String, String>? query,
    Object? body,
  }) async {
    final token = await authStore.getToken();
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: query);
    final headers = <String, String>{
      'Content-Type': 'application/json',
      if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
    };

    final req = http.Request(method, uri);
    req.headers.addAll(headers);
    if (body != null) {
      req.body = jsonEncode(body);
    }

    final res = await _client.send(req);
    final text = await res.stream.bytesToString();
    final json = text.isEmpty ? <String, dynamic>{} : jsonDecode(text);

    if (res.statusCode >= 400) {
      final err = json is Map<String, dynamic> ? json['error'] : null;
      final msg = err is Map<String, dynamic> ? (err['message']?.toString() ?? 'error') : 'error';
      throw Exception(msg);
    }

    return json is Map<String, dynamic> ? json : <String, dynamic>{};
  }

  Future<void> requestOtp(String phone) async {
    await _request('POST', '/auth/request-otp', body: {'phone': phone});
  }

  Future<String> verifyOtp(String phone, String code) async {
    final json = await _request('POST', '/auth/verify-otp', body: {'phone': phone, 'code': code});
    return json['accessToken']?.toString() ?? '';
  }

  Future<Map<String, dynamic>> getMe() async {
    return _request('GET', '/me');
  }

  Future<Map<String, dynamic>> createPlace({
    required String name,
    required String city,
    String? area,
  }) async {
    return _request('POST', '/places', body: {'name': name, 'city': city, 'area': area});
  }

  Future<Map<String, dynamic>> createVisit({
    required String placeId,
    required String dayPart,
    required String highlights,
    required String pitfalls,
    required String revisitIntent,
    String publishStatus = 'private',
  }) async {
    return _request(
      'POST',
      '/visits',
      body: {
        'placeId': placeId,
        'dayPart': dayPart,
        'publishStatus': publishStatus,
        'highlights': highlights,
        'pitfalls': pitfalls,
        'revisitIntent': revisitIntent,
      },
    );
  }

  Future<List<Map<String, dynamic>>> listMyVisits() async {
    final json = await _request('GET', '/visits/mine');
    final items = json['items'];
    if (items is List) {
      return items.whereType<Map<String, dynamic>>().toList();
    }
    return <Map<String, dynamic>>[];
  }

  Future<List<Map<String, dynamic>>> listPublicVisits() async {
    final json = await _request('GET', '/public/visits');
    final items = json['items'];
    if (items is List) {
      return items.whereType<Map<String, dynamic>>().toList();
    }
    return <Map<String, dynamic>>[];
  }

  Future<List<Map<String, dynamic>>> listFavorites() async {
    final json = await _request('GET', '/favorites');
    final items = json['items'];
    if (items is List) {
      return items.whereType<Map<String, dynamic>>().toList();
    }
    return <Map<String, dynamic>>[];
  }

  Future<void> favorite(String visitId) async {
    await _request('POST', '/favorites', body: {'visitId': visitId});
  }

  Future<void> unfavorite(String visitId) async {
    await _request('DELETE', '/favorites/$visitId');
  }

  Future<void> reportVisit(String visitId, String reason, {String? description}) async {
    await _request(
      'POST',
      '/reports',
      body: {
        'targetType': 'visit',
        'targetId': visitId,
        'reason': reason,
        'description': description,
      },
    );
  }

  Future<void> submitFeedback(String type, String message) async {
    await _request('POST', '/feedbacks', body: {'type': type, 'message': message});
  }
}

