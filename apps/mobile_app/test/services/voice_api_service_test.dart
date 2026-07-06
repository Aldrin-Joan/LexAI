import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_application_1/services/voice_api_service.dart';

void main() {
  group('VoiceApiService.normalizeChatResponse', () {
    test('Normalizes legacy response shape', () {
      final raw = {
        'response': 'Hello',
        'sources': ['s1', 's2'],
      };

      final normalized = VoiceApiService.normalizeChatResponse(raw);

      expect(normalized['response'], 'Hello');
      expect(normalized['sources'], ['s1', 's2']);
      expect(normalized.containsKey('session_id'), isFalse);
    });

    test('Normalizes new backend response shape', () {
      final raw = {
        'answer': 'Legal advice',
        'session_id': 'abc123',
        'precedents': [
          {'id': 'x1', 'title': 'Case X1'},
        ],
      };

      final normalized = VoiceApiService.normalizeChatResponse(raw);

      expect(normalized['response'], 'Legal advice');
      expect(normalized['session_id'], 'abc123');
      expect(normalized['precedents'], isNotEmpty);
    });

    test('Throws on unexpected schema', () {
      final raw = {'foo': 'bar'};

      expect(
        () => VoiceApiService.normalizeChatResponse(raw),
        throwsA(isA<Exception>()),
      );
    });
  });
}
