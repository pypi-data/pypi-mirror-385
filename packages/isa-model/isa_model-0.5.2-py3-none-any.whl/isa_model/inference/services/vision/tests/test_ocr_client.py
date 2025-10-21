#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test OCR Client using ISA Model Client
Tests the SuryaOCR service for text extraction through the unified client.
"""

import asyncio
import logging
from typing import Dict, Any

from isa_model.client import ISAModelClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRTester:
    """Test client for SuryaOCR service using ISA Model Client"""
    
    def __init__(self):
        self.client = ISAModelClient()
        
        # Test configuration for OCR service
        self.test_config = {
            "model": "isa-suryaocr",
            "provider": "isa", 
            "task": "extract",
            "input_image": "isa_model/inference/services/vision/tests/contract.png"
        }
    
    async def test_ocr_extraction(self) -> Dict[str, Any]:
        """Test OCR text extraction from contract image using unified client"""
        logger.info("Testing OCR text extraction via unified client...")
        
        try:
            config = self.test_config
            
            result = await self.client.invoke(
                input_data=config["input_image"],
                task=config["task"],
                service_type="vision",
                model=config["model"],
                provider=config["provider"],
                languages=["en", "zh"]
            )
            
            if result.get("success"):
                response = result["result"]
                logger.info(f"OCR extraction successful")
                
                # Get extracted text
                extracted_text = response.get('text', '')
                text_length = len(extracted_text)
                logger.info(f"Text extracted: {text_length} characters")
                
                # Get cost information
                cost = response.get('metadata', {}).get('billing', {}).get('estimated_cost_usd', 0)
                logger.info(f"Cost: ${cost:.6f}")
                
                # Log first 200 characters of extracted text for verification
                if extracted_text:
                    preview_text = extracted_text[:200] + "..." if text_length > 200 else extracted_text
                    logger.info(f"Text preview: {preview_text}")
                
                return {
                    "status": "success",
                    "result": response,
                    "metadata": result.get("metadata", {}),
                    "text_length": text_length,
                    "cost": cost
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"OCR extraction failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"OCR extraction failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_direct_vision_service(self) -> Dict[str, Any]:
        """Test OCR using direct ISA vision service call"""
        logger.info("Testing direct ISA vision service OCR...")
        
        try:
            from isa_model.inference import AIFactory
            
            # Get ISA vision service directly
            vision = AIFactory().get_vision(provider="isa")
            
            # Extract text using SuryaOCR
            result = await vision.extract_text(
                self.test_config["input_image"],
                languages=["en", "zh"]
            )
            
            if result.get('success'):
                logger.info(f"Direct SuryaOCR successful")
                
                # Get extracted text from text_results array
                text_results = result.get('text_results', [])
                extracted_text = ' '.join([item.get('text', '') for item in text_results])
                text_length = len(extracted_text)
                logger.info(f"Text extracted: {text_length} characters from {len(text_results)} detected regions")
                
                # Get cost information
                cost = result.get('billing', {}).get('estimated_cost_usd', 0)
                logger.info(f"Cost: ${cost:.6f}")
                
                # Count Chinese and English characters
                chinese_chars = sum(1 for char in extracted_text if '\u4e00' <= char <= '\u9fff')
                english_chars = sum(1 for char in extracted_text if char.isalpha() and ord(char) < 256)
                logger.info(f"Chinese characters: {chinese_chars}, English characters: {english_chars}")
                
                # Log text preview (first few items)
                if text_results:
                    sample_texts = [item.get('text', '') for item in text_results[:5]]
                    logger.info(f"Sample extracted text: {sample_texts}")
                
                return {
                    "status": "success", 
                    "result": result,
                    "text_length": text_length,
                    "cost": cost
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Direct SuryaOCR failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"Direct SuryaOCR failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_chinese_and_english_ocr(self) -> Dict[str, Any]:
        """Test OCR with Chinese and English language support"""
        logger.info("Testing Chinese and English OCR support...")
        
        try:
            from isa_model.inference import AIFactory
            
            vision = AIFactory().get_vision(provider="isa")
            
            # Test with both Chinese and English languages
            result = await vision.extract_text(
                self.test_config["input_image"],
                languages=["zh", "en"]  # Chinese first, then English
            )
            
            if result.get('success'):
                logger.info(f"Multi-language OCR successful")
                
                extracted_text = result.get('text', '')
                text_length = len(extracted_text)
                logger.info(f"Text length: {text_length}")
                
                # Check for Chinese characters
                chinese_chars = sum(1 for char in extracted_text if '\u4e00' <= char <= '\u9fff')
                english_chars = sum(1 for char in extracted_text if char.isalpha() and ord(char) < 256)
                
                logger.info(f"Chinese characters detected: {chinese_chars}")
                logger.info(f"English characters detected: {english_chars}")
                
                # Get cost
                cost = result.get('billing', {}).get('estimated_cost_usd', 0)
                logger.info(f"Cost: ${cost:.6f}")
                
                return {
                    "status": "success",
                    "result": result,
                    "text_length": text_length,
                    "chinese_chars": chinese_chars,
                    "english_chars": english_chars,
                    "cost": cost
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Multi-language OCR failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"Multi-language OCR failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_all_ocr_methods(self) -> Dict[str, Dict[str, Any]]:
        """Test OCR functionality"""
        logger.info("Starting SuryaOCR test using ISA Model Client...")
        
        results = {}
        
        # Test only the direct vision service (most comprehensive)
        tests = [
            ("suryaocr_extraction", self.test_direct_vision_service)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running test: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                result = await test_func()
                results[test_name] = result
                
                if result.get("status") == "success":
                    logger.info(f" {test_name} PASSED")
                else:
                    logger.error(f"L {test_name} FAILED: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"L {test_name} FAILED with exception: {e}")
                results[test_name] = {"status": "error", "error": str(e)}
        
        # Summary
        logger.info(f"\n{'='*50}")
        logger.info("TEST SUMMARY")
        logger.info(f"{'='*50}")
        
        passed = sum(1 for r in results.values() if r.get("status") == "success")
        total = len(results)
        
        logger.info(f"Passed: {passed}/{total}")
        
        for test_name, result in results.items():
            status = " PASS" if result.get("status") == "success" else "L FAIL"
            logger.info(f"{test_name}: {status}")
        
        return results
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get health status of the client and services"""
        logger.info("Checking service health...")
        
        try:
            health = await self.client.health_check()
            return health
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}

async def main():
    """Main test function"""
    tester = OCRTester()
    
    # Get service health
    logger.info("Checking service health...")
    health = await tester.get_service_health()
    logger.info(f"Service health: {health}")
    
    # Run all tests
    results = await tester.test_all_ocr_methods()
    
    # Calculate total cost
    total_cost = 0.0
    for test_name, result in results.items():
        if result.get("status") == "success":
            cost = result.get("cost", 0.0)
            total_cost += cost
    
    logger.info(f"\nTotal cost for all OCR tests: ${total_cost:.6f}")
    
    # Summary of text extraction results
    logger.info(f"\n{'='*50}")
    logger.info("TEXT EXTRACTION SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        if result.get("status") == "success":
            text_length = result.get("text_length", 0)
            cost = result.get("cost", 0)
            logger.info(f"{test_name}: {text_length} chars extracted, ${cost:.6f}")
            
            # Show language breakdown if available
            if "chinese_chars" in result and "english_chars" in result:
                logger.info(f"  - Chinese: {result['chinese_chars']} chars")
                logger.info(f"  - English: {result['english_chars']} chars")
    
    return results

if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())