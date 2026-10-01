export interface AdminUser {
    id: number;
    username: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface ApiError {
    detail: string;
}
