import Foundation

struct Product: Identifiable, Codable {
    let id: String
    let name: String
    let description: String
    let price: Double
    let score: Double?
    
    // MAPPING: Take the strange names from the JSON and assign them to my variables
    enum CodingKeys: String, CodingKey {
        case id = "_id"
        case name = "title"
        case description
        case price
        case score
    }
}
