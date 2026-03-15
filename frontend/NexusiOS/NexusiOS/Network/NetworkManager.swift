import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    
    // Nginx is our doorstep address
    private let baseURL = "http://localhost"
    
    private init() {}
    
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
