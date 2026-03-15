import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    
    // Nginx is our doorstep address
    private let baseURL = "http://localhost"
    
    private init() {}
    
    // MARK: - Authentication (Kimlik Doğrulama) İşlemleri
    // 1. KULLANICI KAYDI (REGISTER)
    func registerUser(credentials: AuthRequest) async throws {
        // Gidilecek adres
        guard let url = URL(string: "\(baseURL)/register") else {
            throw URLError(.badURL)
        }
        
        // Bu sefer sadece adres vermiyoruz, kuryenin eline bir "Paket" veriyoruz (POST İsteği)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type") // İçerik JSON diyoruz
        
        // Swift objesini JSON'a çevirip kuryenin çantasına (httpBody) koyuyoruz
        request.httpBody = try JSONEncoder().encode(credentials)
        
        // Kurye yola çıkıyor!
        let (_, response) = try await URLSession.shared.data(for: request)
        
        // Garson bize 200 (veya 201 Created) döndü mü kontrol ediyoruz
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
        
        // Kayıt başarılıysa bir şey döndürmemize gerek yok, işlem tamamdır!
    }
    
    // 2. KULLANICI GİRİŞİ (LOGIN)
    func loginUser(credentials: AuthRequest) async throws -> AuthResponse {
        guard let url = URL(string: "\(baseURL)/login") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(credentials)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        // Giriş başarılıysa, Garsonun verdiği o karmaşık bileti (JSON) bizim AuthResponse kalıbına çeviriyoruz
        let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
        return authResponse
    }
    
    
    
    // MARK: - FetchProducts
    
    func fetchProducts() async throws -> [Product] {
        
        // 1. Gidilecek tam adresi oluşturuyoruz (Örn: http://localhost/products)
        guard let url = URL(string: "\(baseURL)/products") else {
            throw URLError(.badURL) // URL hatalıysa işlemi durdur
        }
        
        // 2. Kargocu (URLSession) yola çıkıyor ve Nginx kapısını çalıyor!
        let (data, response) = try await URLSession.shared.data(from: url)
        
        // 3. Kapıdan dönen cevap 200 (Başarılı) değilse hata fırlat
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        // 4. Nginx'ten gelen o karmaşık JSON metnini, bizim yazdığımız 'Product' (Model) yapısına çevir (Decode)
        let decoder = JSONDecoder()
        let products = try decoder.decode([Product].self, from: data)
        
        return products // Çevrilmiş tertemiz ürün listesini geri döndür
    }
}
