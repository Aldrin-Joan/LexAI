import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Simple UI state for the client dashboard navigation index using Notifier.
class ClientNavController extends Notifier<int> {
  @override
  int build() => 0;

  void setIndex(int index) => state = index;
}

final clientNavIndexProvider = NotifierProvider<ClientNavController, int>(
  ClientNavController.new,
);
