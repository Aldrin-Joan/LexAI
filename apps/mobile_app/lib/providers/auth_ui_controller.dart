import 'package:flutter_riverpod/flutter_riverpod.dart';

enum AuthMode { login, signup }

enum UserRole { client, lawyer }

class AuthUiState {
  final AuthMode mode;
  final UserRole role;

  const AuthUiState({required this.mode, required this.role});

  AuthUiState copyWith({AuthMode? mode, UserRole? role}) {
    return AuthUiState(mode: mode ?? this.mode, role: role ?? this.role);
  }
}

class AuthUiController extends Notifier<AuthUiState> {
  @override
  AuthUiState build() {
    return const AuthUiState(mode: AuthMode.login, role: UserRole.client);
  }

  void toggleMode() {
    state = state.copyWith(
      mode: state.mode == AuthMode.login ? AuthMode.signup : AuthMode.login,
    );
  }

  void selectRole(UserRole role) {
    state = state.copyWith(role: role);
  }
}

final authUiProvider = NotifierProvider<AuthUiController, AuthUiState>(
  AuthUiController.new,
);
