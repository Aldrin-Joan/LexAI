import 'dart:io';
import 'package:dio/dio.dart';

/// Service for communicating with the FastAPI backend.
///
/// Supports both the legacy `/legal` backend and the newer `Legal_AI_Backend--main` endpoints.
class VoiceApiService {
  // 10.0.2.2 = localhost on Android emulator.
  // For a real device on the same WiFi, set this to your machine's local IP,
  // e.g. "http://192.168.1.42:8001".
  // Override with `--dart-define=API_BASE_URL=https://host:port` in build/test.
  static const String _defaultBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8001',
  );

  static String get baseUrl => _defaultBaseUrl;

  static final Dio _dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 120), // long running operations
      responseType: ResponseType.json,
    ),
  );

  static String get audioBaseUrl => baseUrl;

  /// Normalize both old and new AI chat response formats.
  ///
  /// - Legacy '{response, sources}' -> {response, sources}
  /// - New '{answer, session_id, precedents}' -> {response, sources}
  /// Public wrapper for normalization, useful for unit testing.
  static Map<String, dynamic> normalizeChatResponse(Map<String, dynamic> raw) {
    return _normalizeChatResponse(raw);
  }

  static Map<String, dynamic> _normalizeChatResponse(Map<String, dynamic> raw) {
    if (raw.containsKey('answer')) {
      return {
        'response': raw['answer'] ?? '',
        'session_id': raw['session_id'],
        'precedents': raw['precedents'],
      };
    }
    if (raw.containsKey('response')) {
      return raw;
    }
    throw Exception('Unexpected chat response schema: $raw');
  }

  /// Send a plain-text message to the active AI chat endpoint.
  ///
  /// Connects to Legal_AI_Backend--main `/chat` and falls back to `/legal/ai-chat`.
  static Future<Map<String, dynamic>> sendTextQuery(String message) async {
    if (message.trim().isEmpty) {
      throw ArgumentError.value(message, 'message', 'must be non-empty');
    }

    Response response;
    try {
      response = await _dio.post('/chat', data: {'query': message});
    } on DioError catch (e) {
      if (e.response != null && e.response!.statusCode == 404) {
        // Fallback for legacy backend path
        response = await _dio.post(
          '/legal/ai-chat',
          data: {'message': message},
        );
      } else {
        rethrow;
      }
    }

    if (response.statusCode == 200) {
      final data = response.data;
      if (data is Map<String, dynamic>) {
        return _normalizeChatResponse(data);
      }
      throw Exception(
        'Unsupported response type from backend: ${data.runtimeType}',
      );
    } else {
      throw Exception(
        'Text query failed: ${response.statusCode} ${response.statusMessage}',
      );
    }
  }

  /// Optional: search for precedents by text query.
  static Future<List<Map<String, dynamic>>> searchCases(
    String query, {
    int limit = 5,
  }) async {
    if (query.trim().isEmpty) {
      throw ArgumentError.value(query, 'query', 'must be non-empty');
    }

    final response = await _dio.post(
      '/search',
      data: {'query': query, 'limit': limit},
    );

    if (response.statusCode == 200) {
      final data = response.data;
      if (data is List) {
        return data.cast<Map<String, dynamic>>();
      }
      throw Exception('Unexpected search response schema: ${data.runtimeType}');
    }
    throw Exception('Search failed: ${response.statusCode}');
  }

  /// Send an audio file to the backend voice-query endpoint.
  ///
  /// This continues to support the legacy `/legal/voice-query` path.
  static Future<Map<String, dynamic>> sendVoiceQuery(File audioFile) async {
    if (!audioFile.existsSync()) {
      throw ArgumentError.value(
        audioFile.path,
        'audioFile',
        'file does not exist',
      );
    }

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        audioFile.path,
        filename: audioFile.path.split(Platform.pathSeparator).last,
      ),
    });

    final response = await _dio.post('/legal/voice-query', data: formData);

    if (response.statusCode == 200) {
      final data = response.data;
      if (data is Map<String, dynamic>) {
        return data;
      }
      throw Exception('Unexpected voice response type: ${data.runtimeType}');
    } else {
      throw Exception(
        'Voice query failed: ${response.statusCode} ${response.statusMessage}',
      );
    }
  }

  /// Build the full audio URL from the relative path returned by the backend.
  static String buildAudioUrl(String relativeAudioUrl) {
    return '$audioBaseUrl$relativeAudioUrl';
  }
}
