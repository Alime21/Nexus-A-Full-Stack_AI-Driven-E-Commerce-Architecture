import SwiftUI

struct ContentView: View {
    // 1. Orkestra Şefimizi (ViewModel) sahneye davet ediyoruz.
    // @StateObject: View'e "Bu şefi dinle, o ne derse ekranı ona göre baştan çiz" der.
    @StateObject private var viewModel = ProductListViewModel()
    
    var body: some View {
        NavigationView {
            Group {
                // DURUM 1: Veriler internetten iniyorsa yükleniyor çarkı göster
                if viewModel.isLoading {
                    ProgressView("Ürünler Yükleniyor...")
                        .scaleEffect(1.2)
                }
                // DURUM 2: Nginx kapalıysa veya hata varsa kırmızı bir hata mesajı bas
                else if let errorMessage = viewModel.errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.red)
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .multilineTextAlignment(.center)
                            .padding()
                    }
                }
                // DURUM 3: Her şey yolundaysa ürünleri şık bir listede göster
                else {
                    List(viewModel.products) { product in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(product.name)
                                .font(.headline)
                            
                            Text(product.description)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                                .lineLimit(2) // Açıklama çok uzunsa 2 satırda kesip sonuna ... koyar
                            
                            Text("\(product.price, specifier: "%.2f") TL")
                                .font(.headline)
                                .foregroundColor(.blue)
                                .bold()
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Nexus Mağaza") // Uygulamanın en üstündeki şık başlık
            
            // Ekran kullanıcıya görünür görünmez ViewModel'e "Hadi verileri getir!" emrini veriyoruz
            .task {
                viewModel.loadProducts()
            }
        }
    }
}

// Sağ taraftaki küçük telefon önizlemesi (Canvas) için
#Preview {
    ContentView()
}
