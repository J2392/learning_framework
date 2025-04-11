"""
Kiểm tra hiệu năng các thành phần trong ứng dụng
"""
import os
import sys
import unittest
import asyncio
import json
import time
import logging
from statistics import mean, stdev
import datetime
from unittest import mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_performance')

# Create results directory
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bench_results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# Try to import modules
try:
    from analyzers.perplexity_analyzer import PerplexityAnalyzer
    from mocks.mock_api import MockPerplexityAPI
    from config import Config
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"Lỗi import module: {e}")
    raise

# Sample texts with different lengths
SAMPLE_TEXT_SHORT = """
Artificial intelligence (AI) is revolutionizing education. It enables personalized learning
experiences and provides immediate feedback to students. Teachers can use AI to automate
routine tasks and focus more on individual student needs.
"""

SAMPLE_TEXT_MEDIUM = """
Climate change poses significant challenges to global ecosystems and human societies.
Rising temperatures lead to more extreme weather events, including droughts, floods, and
storms. These changes affect agriculture, water resources, and public health worldwide.
Scientists agree that reducing greenhouse gas emissions is essential to mitigate the worst
effects of climate change. Renewable energy adoption, improved energy efficiency, and
sustainable land management practices are key strategies for addressing this global crisis.
"""

SAMPLE_TEXT_LONG = """
The history of computing spans thousands of years, from ancient calculating devices to modern 
supercomputers and artificial intelligence systems. Early computational tools included the abacus, 
developed independently across several ancient civilizations, and mechanical calculating machines 
like Blaise Pascal's Pascaline in the 17th century and Charles Babbage's Difference Engine in the 
19th century.

The theoretical foundations for modern computing were laid in the early 20th century through the 
work of mathematicians and logicians like Alan Turing, whose concept of a universal computing 
machine (the Turing machine) provided a mathematical model for all computers. During World War II, 
the need for complex calculations for code-breaking and weapons development accelerated progress in 
computing technology, leading to machines like the British Colossus and the American ENIAC.

The post-war era saw rapid advancements in computing hardware, from vacuum tubes to transistors to 
integrated circuits, following Moore's Law – the observation that the number of transistors on a 
microchip doubles approximately every two years, while the cost halves. This exponential growth in 
computing power enabled increasingly sophisticated applications and the miniaturization of computers 
from room-sized mainframes to personal computers and, eventually, smartphones.

Parallel to hardware development, software evolved from machine code and assembly language to 
high-level programming languages that made computing more accessible. The development of operating 
systems, graphical user interfaces, and networking technologies like the Internet transformed how 
people interact with computers and with each other.

In recent decades, computing has been shaped by trends like cloud computing, which provides 
scalable, on-demand resources; mobile computing, which has put powerful computers in billions of 
pockets; and the Internet of Things, which connects everyday objects to networks. The field of 
artificial intelligence, after periods of progress and setbacks known as "AI winters," has seen 
remarkable advances in the 21st century through machine learning and deep neural networks, enabling 
computers to perform tasks once thought to require human intelligence, such as image recognition, 
natural language processing, and complex decision-making.
"""

# Text categories by length
TEXT_SAMPLES = {
    "short": SAMPLE_TEXT_SHORT,
    "medium": SAMPLE_TEXT_MEDIUM,
    "long": SAMPLE_TEXT_LONG
}

# Run async function in tests
def run_async(loop, coro):
    """Run coroutine in a specific event loop"""
    if loop.is_closed():
        logger.warning("Attempted to run on a closed loop. Returning None.")
        return None
    return loop.run_until_complete(coro)

class TestPerformance(unittest.TestCase):
    """Kiểm tra hiệu năng"""
    
    @classmethod
    def setUpClass(cls):
        """Thiết lập trước tất cả tests"""
        load_dotenv()
        cls.api_key = os.getenv('PERPLEXITY_API_KEY')
        cls.dev_mode = os.getenv('DEVELOPMENT_MODE', 'True').lower() == 'true'
        cls.model = os.getenv('PERPLEXITY_MODEL', 'sonar')
        
        # Force development mode cho benchmark
        os.environ['DEVELOPMENT_MODE'] = 'True'
        cls.analyzer = PerplexityAnalyzer()
        
        # Danh sách generators để test
        cls.generators = [
            "summary", "key_terms", "questions", 
            "explanations", "practice", "blooms", "analogies"
        ]
        
        # Thiết lập cho so sánh giữa các phiên bản
        cls.benchmark_results = {}
        
        # Thiết lập mock session
        cls.test_session = mock.MagicMock()
    
    def setUp(self):
        """Thiết lập trước mỗi test, tạo event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.text_size = "short"  # Default size
        self.text = TEXT_SAMPLES[self.text_size]
        self.iterations = 3  # Default iterations
    
    def tearDown(self):
        """Dọn dẹp sau mỗi test, đóng event loop"""
        self.loop.close()
        asyncio.set_event_loop(None)
        
    def save_results(self, results, prefix="benchmark"):
        """Lưu kết quả benchmark vào file"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Kết quả benchmark đã được lưu vào {filepath}")
        return filepath
    
    def _get_generator_function(self, generator_name):
        """Lấy hàm generator theo tên"""
        generator_functions = {
            "summary": self.analyzer._generate_summary,
            "key_terms": self.analyzer._generate_key_terms,
            "questions": self.analyzer._generate_questions,
            "explanations": self.analyzer._generate_explanations,
            "practice": self.analyzer._generate_practice_questions,
            "blooms": self.analyzer._generate_blooms_questions,
            "analogies": self.analyzer._generate_analogies
        }
        
        if generator_name not in generator_functions:
            raise ValueError(f"Generator không hợp lệ: {generator_name}")
        
        return generator_functions[generator_name]
    
    async def benchmark_generator(self, generator_name, text, iterations=3):
        """Benchmark a single generator by calling analyze()"""
        logger.info(f"Benchmark generator: {generator_name} via analyze() with text size: {len(text)} chars, {iterations} iterations")
        
        # Ensure we are in dev mode for this benchmark approach
        self.assertTrue(Config.DEVELOPMENT_MODE, "Benchmark tests should run in DEVELOPMENT_MODE=True")
        
        execution_times = []
        start_times = []
        end_times = []
        results = []
        result_sizes = []
        result_types = []
        
        for i in range(iterations):
            # Clear cache if enabled to get consistent timing
            if Config.CACHE_ENABLED:
                 self.analyzer._cache = {}
                 
            start_time = time.time()
            start_times.append(start_time)
            
            # Call analyze and extract the specific generator result
            full_result = await self.analyzer.analyze(text)
            result = full_result.get(generator_name, []) # Get result or empty list
            results.append(result)
            result_sizes.append(len(str(result)))
            result_types.append(type(result).__name__)
            
            end_time = time.time()
            end_times.append(end_time)
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            logger.info(f"Iteration {i+1}/{iterations}: {execution_time:.3f} seconds")
            
            await asyncio.sleep(0.1) # Small delay between iterations
            
        # Calculate stats
        avg_time = mean(execution_times) if execution_times else 0
        std_dev = stdev(execution_times) if len(execution_times) > 1 else 0
        
        logger.info(f"Benchmark {generator_name} (via analyze) - Avg: {avg_time:.3f}s, StDev: {std_dev:.3f}s")
        
        return {
            "generator": generator_name,
            "method_called": "analyze",
            "text_length": len(text),
            "text_type": self.text_size,
            "iterations": iterations,
            "times": execution_times,
            "start_times": start_times,
            "end_times": end_times,
            "avg_time": avg_time,
            "std_dev": std_dev,
            "result_types": result_types,
            "result_sizes": result_sizes
        }
    
    async def benchmark_analyze_method(self, text, iterations=3):
        """Benchmark phương thức analyze"""
        logger.info(f"Benchmark phương thức analyze với text size: {len(text)} ký tự, {iterations} lần lặp")
        
        execution_times = []
        results = []
        
        for i in range(iterations):
            # Xóa cache trước mỗi lần gọi
            self.analyzer._cache = {}
            
            # Đo thời gian
            start_time = time.time()
            
            # Gọi analyze
            result = await self.analyzer.analyze(text)
            results.append(result)
            
            # Tính thời gian thực thi
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
            
            logger.info(f"Lần {i+1}/{iterations}: {execution_time:.3f} giây")
            
            # Tạm dừng giữa các lần chạy
            await asyncio.sleep(0.1)
        
        # Wait for tasks to complete if necessary
        # self.loop.run_until_complete(asyncio.sleep(0)) # Removed
        
        # Tính toán các chỉ số thống kê
        avg_time = mean(execution_times)
        if len(execution_times) > 1:
            std_dev = stdev(execution_times)
        else:
            std_dev = 0
        
        # Log kết quả
        logger.info(f"analyze method - Trung bình: {avg_time:.3f}s, Độ lệch chuẩn: {std_dev:.3f}s")
        
        # Trả về kết quả chi tiết
        return {
            "method": "analyze",
            "text_length": len(text),
            "text_type": self.text_size,
            "iterations": iterations,
            "times": execution_times,
            "avg_time": avg_time,
            "std_dev": std_dev,
            "result_fields": list(results[0].keys()) if results and isinstance(results[0], dict) else [],
            "result_sizes": [len(str(r)) for r in results]
        }
    
    async def benchmark_all_generators(self, text_size="short", generators=None, iterations=3):
        """Benchmark tất cả generators với một kích thước text"""
        if generators is None:
            generators = self.generators[:4]  # Mặc định chạy 4 generators đầu tiên để tiết kiệm thời gian
        
        self.text_size = text_size
        self.text = TEXT_SAMPLES[text_size]
        self.iterations = iterations
        
        logger.info(f"Benchmark tất cả generators với text size: {text_size}, {iterations} lần lặp")
        logger.info(f"Đang chạy generators: {', '.join(generators)}")
        
        results = {}
        all_benchmarks = []
        
        for generator_name in generators:
            benchmark = await self.benchmark_generator(generator_name, self.text, iterations)
            results[generator_name] = benchmark
            all_benchmarks.append(benchmark)
        
        # Wait for tasks to complete
        # self.loop.run_until_complete(asyncio.sleep(0)) # Removed
        
        # Tạo báo cáo so sánh
        comparison = {
            "text_size": text_size,
            "text_length": len(self.text),
            "iterations": iterations,
            "benchmarks": all_benchmarks,
            "summary": {generator: results[generator]["avg_time"] for generator in generators}
        }
        
        # Lưu kết quả
        self.save_results(comparison, f"benchmark_{text_size}")
        
        return comparison
    
    def test_benchmark_summary_generator_by_size(self):
        """Benchmark generator summary with different text sizes"""
        logger.info("Benchmark generator summary with different text sizes")
        
        results = {}
        
        # Test với các kích thước text khác nhau
        for text_size in ["short", "medium"]:  # Bỏ qua "long" để tiết kiệm thời gian
            self.text_size = text_size
            self.text = TEXT_SAMPLES[text_size]
            
            # benchmark_generator now calls analyze()
            benchmark = run_async(self.loop, self.benchmark_generator("summary", self.text, 2))
            results[text_size] = benchmark
            
            # Kiểm tra thời gian thực thi
            self.assertGreaterEqual(benchmark["avg_time"], 0, "Thời gian thực thi phải không âm")
            self.assertLess(benchmark["avg_time"], 10, "Thời gian thực thi quá lâu (>10s)")
        
        # So sánh hiệu năng với các kích thước khác nhau
        if "medium" in results and "short" in results:
            short_time = results["short"]["avg_time"]
            medium_time = results["medium"]["avg_time"]
            ratio = medium_time / short_time if short_time > 1e-9 else float('inf')
            logger.info(f"Tỷ lệ thời gian thực thi medium/short: {ratio:.2f}")
            
            # Chỉ kiểm tra tỷ lệ nếu không ở development mode
            if not Config.DEVELOPMENT_MODE:
                self.assertGreaterEqual(ratio, 0.5, "Text dài hơn phải mất ít nhất 50% thời gian của text ngắn (prod mode)")
            else:
                logger.info("Skipping ratio assertion in development mode")

        # Lưu kết quả
        self.save_results(results, "benchmark_summary_by_size")
    
    def test_benchmark_analyze_method(self):
        """Benchmark phương thức analyze"""
        logger.info("Benchmark phương thức analyze với text ngắn")
        
        benchmark = run_async(self.loop, self.benchmark_analyze_method(self.text, 2))
        
        # Kiểm tra kết quả
        self.assertGreater(benchmark["avg_time"], 0, "Thời gian thực thi phải lớn hơn 0")
        self.assertGreaterEqual(len(benchmark["result_fields"]), 3, "Phải có ít nhất 3 trường trong kết quả")
        
        # Lưu kết quả
        self.save_results(benchmark, "benchmark_analyze")
    
    def test_benchmark_compare_generators(self):
        """So sánh hiệu năng giữa các generators"""
        logger.info("So sánh hiệu năng giữa các generators")
        
        # Giới hạn generators để kiểm tra nhanh
        test_generators = ["summary", "key_terms"]
        
        results = run_async(self.loop, self.benchmark_all_generators("short", test_generators, 2))
        
        # Kiểm tra kết quả
        for generator in test_generators:
            self.assertIn(generator, results["summary"], f"Thiếu kết quả cho generator {generator}")
            
        # In bảng so sánh
        logger.info("Bảng so sánh hiệu năng generators:")
        for generator, avg_time in results["summary"].items():
            logger.info(f"  {generator}: {avg_time:.3f}s")
    
    @unittest.skipIf(os.getenv('QUICK_TEST', 'True').lower() == 'true', 
                    "Bỏ qua test toàn diện khi chạy QUICK_TEST")
    def test_comprehensive_benchmark(self):
        """Benchmark toàn diện với nhiều generators và kích thước text"""
        logger.info("Benchmark toàn diện với nhiều generators và kích thước text")
        
        # Test với 3 kích thước text, 4 generators, 3 lần lặp mỗi loại
        all_results = {}
        generators = ["summary", "key_terms", "questions", "explanations"]
        
        for text_size in ["short", "medium", "long"]:
            results = run_async(self.loop, self.benchmark_all_generators(text_size, generators, 3))
            all_results[text_size] = results
        
        # Tạo báo cáo tổng hợp
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": {
                "development_mode": self.dev_mode,
                "model": self.model,
            },
            "generators": generators,
            "text_sizes": list(all_results.keys()),
            "results": all_results
        }
        
        # Lưu kết quả
        self.save_results(summary, "comprehensive_benchmark")
        
        # In bảng tổng hợp
        logger.info("\nBảng tổng hợp hiệu năng theo text size và generator:")
        for text_size, results in all_results.items():
            logger.info(f"\nText size: {text_size}")
            for generator, avg_time in results['summary'].items():
                logger.info(f"  {generator}: {avg_time:.3f}s")
    
    def test_benchmark_cold_vs_warm_cache(self):
        """So sánh hiệu năng giữa cold cache và warm cache bằng cách gọi analyze()"""
        logger.info("So sánh hiệu năng cache bằng cách gọi analyze()")
        
        # Ensure we are in dev mode for consistent mock results
        self.assertTrue(Config.DEVELOPMENT_MODE, "Cache benchmark should run in DEVELOPMENT_MODE=True")

        # Cold cache - First call to analyze()
        self.analyzer._cache = {} # Ensure cache is empty
        start_time = time.time()
        cold_result = run_async(self.loop, self.analyzer.analyze(self.text))
        cold_time = time.time() - start_time
        
        # Warm cache - Second call with same text
        start_time = time.time()
        warm_result = run_async(self.loop, self.analyzer.analyze(self.text))
        warm_time = time.time() - start_time
        
        # Reset cache for subsequent tests
        self.analyzer._cache = {}
        
        # Cold cache again - After reset (for verification)
        start_time = time.time()
        cold_result2 = run_async(self.loop, self.analyzer.analyze(self.text))
        cold_time2 = time.time() - start_time
        
        # Log results
        logger.info(f"Cold cache analyze() time: {cold_time:.3f}s")
        logger.info(f"Warm cache analyze() time: {warm_time:.3f}s")
        logger.info(f"Cold cache analyze() time (after reset): {cold_time2:.3f}s")
        
        # Check results are identical
        self.assertEqual(cold_result, warm_result, "Cached result differs from original")
        
        # Check cache performance improvement
        # In dev mode, calls are very fast, so warm_time might not be *significantly* less
        # We expect warm_time <= cold_time. Allow a small margin for fluctuations.
        self.assertLessEqual(warm_time, cold_time + 0.01, "Warm cache call took longer than cold cache call") 
        # Optionally, assert warm_time is very small if mocks are fast
        self.assertLess(warm_time, 0.1, "Warm cache call took unexpectedly long (>0.1s)")
        logger.info(f"Cache improvement ratio (Cold/Warm): {cold_time / warm_time if warm_time > 0 else 'inf'}")

        # Lưu kết quả
        cache_results = {
            "method_called": "analyze",
            "text_length": len(self.text),
            "cold_time": cold_time,
            "warm_time": warm_time,
            "cold_time_after_reset": cold_time2,
            "improvement_factor": cold_time / warm_time if warm_time > 0 else None,
            "results_equal": str(cold_result) == str(warm_result)
        }
        
        self.save_results(cache_results, "cache_benchmark")
    
    def test_memory_usage(self):
        """Test hiệu quả sử dụng bộ nhớ"""
        try:
            import psutil
            import gc
        except ImportError:
            logger.warning("Không thể import psutil hoặc gc, bỏ qua test memory usage")
            self.skipTest("Thiếu thư viện psutil")
        
        logger.info("Kiểm tra hiệu quả sử dụng bộ nhớ")
        
        # Lấy process hiện tại
        process = psutil.Process(os.getpid())
        
        # Force garbage collection
        gc.collect()
        
        # Đo memory trước khi tạo analyzer
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Tạo và sử dụng analyzer
        analyzer = PerplexityAnalyzer()
        result = run_async(self.loop, analyzer.analyze(SAMPLE_TEXT_MEDIUM))
        
        # Đo memory sau khi sử dụng
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        # Tính memory usage
        mem_diff = mem_after - mem_before
        
        # Log kết quả
        logger.info(f"Memory trước: {mem_before:.2f} MB")
        logger.info(f"Memory sau: {mem_after:.2f} MB")
        logger.info(f"Memory sử dụng: {mem_diff:.2f} MB")
        
        # Kiểm tra memory usage
        self.assertLess(mem_diff, 100, "Sử dụng quá nhiều bộ nhớ (>100MB)")
        
        # Lưu kết quả
        memory_results = {
            "memory_before_mb": mem_before,
            "memory_after_mb": mem_after,
            "memory_diff_mb": mem_diff,
            "result_size_chars": len(str(result))
        }
        
        self.save_results(memory_results, "memory_benchmark")

if __name__ == '__main__':
    unittest.main(verbosity=2) 