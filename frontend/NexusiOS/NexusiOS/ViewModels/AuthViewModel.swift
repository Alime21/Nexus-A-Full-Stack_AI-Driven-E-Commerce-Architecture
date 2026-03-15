import Foundation

@MainActor
class AuthViewModel: ObservableObject {
    // Ekranda kullanıcının dolduracağı alanlar
    @Published var email = ""
    @Published var password = ""
    
    // Ekranın durumunu yönetecek değişkenler
    @Published var isLoading = false
    @Published var errorMessage: String? = nil
    @Published var isAuthenticated = false // VIP Bilet başarıyla alındıysa bu 'true' olacak
    
    // Kuryeyi Login için gönderen fonksiyon
    func login() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let credentials = AuthRequest(email: email, password: password)
                let response = try await NetworkManager.shared.loginUser(credentials: credentials)
                
                print(" VIP Bilet (Token) Alındı: \(response.access_token)")
                
                // 1. YENİ KOD: Bileti telefonun güvenli hafızasına (Kasa) kaydediyoruz!
                UserDefaults.standard.set(response.access_token, forKey: "userToken")
                
                // Bu satırı da UI'ı güncellemek için ana iş parçacığında çalışmaya zorluyoruz
                DispatchQueue.main.async {
                    self.isAuthenticated = true
                    self.isLoading = false
                }
                
                self.isAuthenticated = true
                self.isLoading = false
            } catch {
                self.errorMessage = "Giriş başarısız. Lütfen e-posta ve şifrenizi kontrol edin."
                self.isLoading = false
            }
        }
    }
    
    // Kuryeyi Register için gönderen fonksiyon
    func register() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let credentials = AuthRequest(email: email, password: password)
                try await NetworkManager.shared.registerUser(credentials: credentials)
                
                // Kayıt başarılıysa kullanıcıya bilgi veriyoruz
                self.errorMessage = "✅ Kayıt başarılı! Lütfen giriş yapın."
                self.isLoading = false
            } catch {
                self.errorMessage = "Kayıt olunamadı. Bu e-posta zaten kullanımda olabilir veya sunucuya ulaşılamıyor."
                self.isLoading = false
            }
        }
    }
}
