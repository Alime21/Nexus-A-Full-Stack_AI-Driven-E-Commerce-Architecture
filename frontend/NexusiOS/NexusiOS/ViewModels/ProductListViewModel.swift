import Foundation
@MainActor
class ProductListViewModel: ObservableObject {
    
    // @Published sihridir! Bu değişkenlerin içi değiştiği an, ekrana (View) "Hey, yeni veri geldi, kendini güncelle!" diye bağırır.
    @Published var products: [Product] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    
    // Ekran açıldığında çağrılacak olan asıl fonksiyon
    func loadProducts() {
        isLoading = true
        errorMessage = nil
        
        // İnternet işlemleri vakit aldığı için sistemi kitlemesin diye bir 'Task' (Arka plan işi) başlatıyoruz
        Task {
            do {
                // Kargocumuzu (NetworkManager) yola çıkarıyoruz!
                let fetchedProducts = try await NetworkManager.shared.fetchProducts()
                
                // Ürünler başarıyla geldiyse listemize ekle ve yükleniyor ikonunu kapat
                self.products = fetchedProducts
                self.isLoading = false
                
            } catch {
                // Eğer Nginx kapalıysa veya hata olursa ekrana basmak üzere hatayı yakala
                self.errorMessage = "Ürünler yüklenirken bir hata oluştu: \(error.localizedDescription)"
                self.isLoading = false
            }
        }
    }
}
