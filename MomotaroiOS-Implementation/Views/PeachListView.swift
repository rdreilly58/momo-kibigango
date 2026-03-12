// Views/PeachListView.swift
// SwiftUI view for displaying list of peaches

import SwiftUI

/// View displaying a list of peaches
struct PeachListView: View {
    @ObservedObject var viewModel: PeachViewModel
    @State private var searchText = ""
    @State private var selectedSort: SortCriteria = .byName
    
    var body: some View {
        NavigationView {
            VStack {
                // Search bar
                SearchBar(text: $searchText)
                    .onChange(of: searchText) { newValue in
                        viewModel.filterPeaches(with: newValue)
                    }
                
                // Sort options
                Picker("Sort by", selection: $selectedSort) {
                    Text("Name").tag(SortCriteria.byName)
                    Text("Ripeness").tag(SortCriteria.byRipeness)
                    Text("Color").tag(SortCriteria.byColor)
                }
                .pickerStyle(.segmented)
                .padding()
                .onChange(of: selectedSort) { newValue in
                    viewModel.sortPeaches(by: newValue)
                }
                
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.red)
                        Text(error)
                            .font(.headline)
                        Button("Retry") {
                            viewModel.loadPeaches()
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding()
                } else {
                    List(viewModel.filteredPeaches) { peach in
                        NavigationLink(destination: PeachDetailView(peach: peach)) {
                            PeachRowView(peach: peach)
                        }
                    }
                    .listStyle(.plain)
                }
                
                Spacer()
            }
            .navigationTitle("Peaches")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

/// Row view for a single peach
struct PeachRowView: View {
    let peach: Peach
    
    var body: some View {
        HStack {
            Circle()
                .fill(colorForPeach(peach.color))
                .frame(width: 50, height: 50)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(peach.name)
                    .font(.headline)
                HStack {
                    Text("Ripeness: \(peach.ripeness)%")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(peach.color)
                        .font(.caption)
                        .padding(4)
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(4)
                }
            }
        }
        .padding(.vertical, 8)
    }
    
    private func colorForPeach(_ colorName: String) -> Color {
        switch colorName.lowercased() {
        case "orange":
            return .orange
        case "red":
            return .red
        case "pink":
            return .pink
        case "yellow":
            return .yellow
        default:
            return .gray
        }
    }
}

/// Detail view for a single peach
struct PeachDetailView: View {
    let peach: Peach
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading) {
                    Text(peach.name)
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("ID: \(peach.id)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 12) {
                InfoRow(label: "Color", value: peach.color)
                InfoRow(label: "Ripeness", value: "\(peach.ripeness)%")
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("Peach Details")
        .navigationBarTitleDisplayMode(.inline)
    }
}

/// Generic info row for displaying key-value pairs
struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .fontWeight(.semibold)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 8)
    }
}

/// Search bar component
struct SearchBar: View {
    @Binding var text: String
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
            
            TextField("Search peaches...", text: $text)
                .textFieldStyle(.roundedBorder)
            
            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
}

#Preview {
    let viewModel = PeachViewModel()
    PeachListView(viewModel: viewModel)
}
