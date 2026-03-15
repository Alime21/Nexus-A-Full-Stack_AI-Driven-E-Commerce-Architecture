import SwiftUI

struct LoginView: View {
    @StateObject private var viewModel = AuthViewModel()
    
    // Ekran Giriş modunda mı yoksa Kayıt modunda mı? Onu tutan küçük bir anahtar
    @State private var isLoginMode = true
    
    var body: some View {
        NavigationView {
            VStack(spacing: 25) {
                
                // Başlık
                Text(isLoginMode ? "Nexus'a Hoş Geldiniz" : "Yeni Hesap Oluştur")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.bottom, 20)
                
                // Form Alanları (E-posta ve Şifre)
                VStack(spacing: 15) {
                    TextField("E-posta adresiniz", text: $viewModel.email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none) // E-postanın ilk harfini büyük yapmasını engeller
                        .padding()
                        .background(Color(UIColor.secondarySystemBackground))
                        .cornerRadius(12)
                    
                    SecureField("Şifreniz", text: $viewModel.password)
                        .padding()
                        .background(Color(UIColor.secondarySystemBackground))
                        .cornerRadius(12)
                }
                .padding(.horizontal)
                
                // Hata veya Başarı Mesajı
                if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(errorMessage.contains("✅") ? .green : .red)
                        .font(.footnote)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                
                // Ana Buton (Giriş Yap / Kayıt Ol)
                Button(action: {
                    if isLoginMode {
                        viewModel.login()
                    } else {
                        viewModel.register()
                    }
                }) {
                    HStack {
                        if viewModel.isLoading {
                            ProgressView()
                                .tint(.white)
                        } else {
                            Text(isLoginMode ? "Giriş Yap" : "Kayıt Ol")
                                .fontWeight(.bold)
                        }
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(12)
                }
                .padding(.horizontal)
                .disabled(viewModel.isLoading) // Yüklenirken butona defalarca basılmasını engeller
                
                Spacer()
                
                // Ekranın altındaki "Hesabın yok mu?" değiştiricisi
                Button(action: {
                    isLoginMode.toggle() // Modu tersine çevirir
                    viewModel.errorMessage = nil // Ekran değişirken eski hataları temizler
                }) {
                    Text(isLoginMode ? "Hesabınız yok mu? Kayıt Olun" : "Zaten hesabınız var mı? Giriş Yapın")
                        .foregroundColor(.blue)
                        .font(.subheadline)
                }
                .padding(.bottom)
            }
        }
    }
}

#Preview {
    LoginView()
}
