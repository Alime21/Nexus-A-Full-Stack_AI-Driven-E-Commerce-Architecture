import SwiftUI

struct RootView: View {
    // @AppStorage: Telefonun kasasındaki "userToken" isimli bileti sürekli dinler.
    // Bilet kasaya girdiği an (veya silindiği an) bu ekran kendini otomatik yeniler!
    @AppStorage("userToken") var userToken: String = ""
    
    var body: some View {
        Group {
            // Trafik Polisi Karar Veriyor:
            if userToken.isEmpty {
                // 1. Kasa boşsa (Bilet yoksa) giriş ekranını göster
                LoginView()
            } else {
                // 2. Kasada bilet varsa direkt mağazayı göster
                ContentView()
            }
        }
        // Sayfalar arası geçiş yaparken o tatlı erime (fade) animasyonunu ekler
        .animation(.easeInOut, value: userToken)
    }
}
