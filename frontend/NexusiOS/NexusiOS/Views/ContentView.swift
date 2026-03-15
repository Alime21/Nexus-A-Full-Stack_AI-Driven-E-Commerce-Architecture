import SwiftUI

struct ContentView: View {
    // 1. Orkestra Şefimizi (ViewModel) sahneye davet ediyoruz.
    // @StateObject: View'e "Bu şefi dinle, o ne derse ekranı ona göre baştan çiz" der.
    @StateObject private var viewModel = ProductListViewModel()
    
    // Ekranda yan yana 2 tane esnek (flexible) sütun olmasını istiyoruz
    let columns = [
            GridItem(.flexible()),
            GridItem(.flexible())
    ]
    
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
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: 16) {
                            ForEach(viewModel.products) { product in
                                // Az önce yazdığımız kartı burada çağırıyoruz
                                ProductCardView(product: product)
                            }
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


// Tek bir ürünün nasıl görüneceğini belirleyen "Kaba İnşaat" Kartımız
struct ProductCardView: View {
    let product: Product
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // İleride buraya gerçek ürün fotoğrafı gelecek, şimdilik yer tutucu (Placeholder) gri bir kutu
            Rectangle()
                .fill(Color.gray.opacity(0.2))
                .aspectRatio(1, contentMode: .fit) // Kare şeklinde kalmasını sağlar
                .cornerRadius(10)
            
            Text(product.name)
                .font(.headline)
                .lineLimit(1) // İsim çok uzunsa tek satırda keser
            
            Text(product.description)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(2)
            
            Text("\(product.price, specifier: "%.2f") TL")
                .font(.subheadline)
                .bold()
                .foregroundColor(.blue)
        }
        .padding()
        // Kartın arka planına hafif bir gölge ve beyazlık vererek belirginleştiriyoruz
        .background(Color(UIColor.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
}
