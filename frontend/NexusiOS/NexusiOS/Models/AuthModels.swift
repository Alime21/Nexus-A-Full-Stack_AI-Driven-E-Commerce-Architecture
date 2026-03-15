import Foundation

// 1. Backend'e göndereceğimiz paket (Kayıt ve Giriş için aynı)
struct AuthRequest: Codable {
    let email: String
    let password: String
}

// 2. Başarılı girişte Backend'den bize gelecek olan VIP Bilet (Token)
struct AuthResponse: Codable {
    let access_token: String
    let token_type: String
}

