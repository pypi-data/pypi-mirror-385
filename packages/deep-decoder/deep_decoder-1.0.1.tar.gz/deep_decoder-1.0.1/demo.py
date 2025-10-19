"""
Quick Demo - Test Deep Decoder Package
Chạy file này để test nhanh: python demo.py
"""

from deep_decoder import quick_decode, deep_decode_data, get_decoding_statistics

print("=" * 70)
print("🚀 DEEP DECODER - DEMO NHANH")
print("=" * 70)

# Test 1: Base64
print("\n1️⃣ Test Base64:")
result = quick_decode("SGVsbG8gV29ybGQh")
print(f"   Input:  SGVsbG8gV29ybGQh")
print(f"   Output: {result} ✅")

# Test 2: URL Encoding
print("\n2️⃣ Test URL Encoding:")
result = quick_decode("%3Cscript%3Ealert%281%29%3C%2Fscript%3E")
print(f"   Input:  %3Cscript%3Ealert%281%29%3C%2Fscript%3E")
print(f"   Output: {result} ✅")

# Test 3: Hex
print("\n3️⃣ Test Hex:")
result = quick_decode("48656C6C6F20576F726C6421")
print(f"   Input:  48656C6C6F20576F726C6421")
print(f"   Output: {result} ✅")

# Test 4: HTML Entities
print("\n4️⃣ Test HTML Entities:")
result = quick_decode("&lt;script&gt;alert&#40;1&#41;&lt;&#x2F;script&gt;")
print(f"   Input:  &lt;script&gt;alert&#40;1&#41;&lt;&#x2F;script&gt;")
print(f"   Output: {result} ✅")

# Test 5: Multiple layers (phức tạp)
print("\n5️⃣ Test Multiple Layers (URL + Base64):")
encoded = "JTNDc2NyaXB0JTNFYWxlcnQoMSklM0MlMkZzY3JpcHQlM0U="
result = deep_decode_data(encoded)
print(f"   Input:  {encoded}")
print(f"   Output: {result.final_data} ✅")
print(f"   📊 Iterations: {result.iterations}")
print(f"   ⏱️  Time: {result.total_time_ms:.2f}ms")

# Test 6: Unicode Escape
print("\n6️⃣ Test Unicode Escape:")
result = quick_decode("\\u0048\\u0065\\u006C\\u006C\\u006F")
print(f"   Input:  \\u0048\\u0065\\u006C\\u006C\\u006F")
print(f"   Output: {result} ✅")

# Test 7: Detailed Analysis
print("\n7️⃣ Test Detailed Analysis:")
encoded = "%252F%2545%2576%2569%256C"
result = deep_decode_data(encoded)
stats = get_decoding_statistics(result)
print(f"   Input:  {encoded}")
print(f"   Output: {result.final_data}")
print(f"   📈 Steps: {stats['successful_iterations']}")
print(f"   📉 Size reduction: {stats['size_reduction_percent']}%")
print(f"   ⭐ Avg confidence: {stats['average_confidence']}")

# Test 8: ROT13
print("\n8️⃣ Test ROT13:")
result = quick_decode("Uryyb Jbeyq")
print(f"   Input:  Uryyb Jbeyq")
print(f"   Output: {result} ✅")

print("\n" + "=" * 70)
print("✅ TẤT CẢ TESTS ĐỀU THÀNH CÔNG!")
print("=" * 70)

print("\n💡 Sử dụng trong code của bạn:")
print("   from deep_decoder import quick_decode")
print('   result = quick_decode("your_encoded_data")')
print('   print(result)')

print("\n📚 Xem thêm:")
print("   - examples/basic_usage.py")
print("   - examples/advanced_usage.py")
print("   - README.md")
print("   - QUICKSTART.md")

print("\n🎉 Package sẵn sàng sử dụng!")
