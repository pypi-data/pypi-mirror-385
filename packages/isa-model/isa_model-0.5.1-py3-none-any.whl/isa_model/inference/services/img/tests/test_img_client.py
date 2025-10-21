#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Image Generation Client using ISA Model Client
Tests the four specialized image generation services through the unified client:
1. FLUX Schnell (text-to-image)
2. FLUX Kontext Pro (image-to-image)  
3. Sticker Maker
4. Face Swap
"""

import asyncio
import logging
from typing import Dict, Any

from isa_model.client import ISAModelClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerationTester:
    """Test client for image generation services using ISA Model Client"""
    
    def __init__(self):
        self.client = ISAModelClient()
        
        # Test configurations for each service
        self.test_configs = {
            "flux_schnell": {
                "model": "flux-schnell",
                "provider": "replicate",
                "task": "generate",
                "prompt": "a cute cat sitting in a garden"
            },
            "flux_kontext": {
                "model": "flux-kontext-pro", 
                "provider": "replicate",
                "task": "img2img",
                "prompt": "transform this into a futuristic cityscape",
                "init_image": "https://replicate.delivery/pbxt/Mb44XIUHkUrmyyH1OP5K1WmFN7SNN0eUSU16A8rBtuXe7eYV/cyberpunk_80s_example.png"
            },
            "sticker_maker": {
                "model": "sticker-maker",
                "provider": "replicate", 
                "task": "generate",
                "prompt": "a cute cat"
            },
            "face_swap": {
                "model": "face-swap",
                "provider": "replicate",
                "task": "face_swap",
                "swap_image": "https://replicate.delivery/pbxt/Mb44Wp0W7Xfa1Pp91zcxDzSSQQz8GusUmXQXi3GGzRxDvoCI/0_1.webp",
                "target_image": "https://replicate.delivery/pbxt/Mb44XIUHkUrmyyH1OP5K1WmFN7SNN0eUSU16A8rBtuXe7eYV/cyberpunk_80s_example.png"
            }
        }
    
    async def test_flux_text_to_image(self) -> Dict[str, Any]:
        """Test FLUX Schnell text-to-image generation"""
        logger.info("Testing FLUX Schnell text-to-image...")
        
        try:
            config = self.test_configs["flux_schnell"]
            
            result = await self.client.invoke(
                input_data=config["prompt"],
                task=config["task"],
                service_type="image",
                model=config["model"],
                provider=config["provider"],
                width=1024,
                height=1024,
                num_inference_steps=4
            )
            
            if result.get("success"):
                response = result["result"]
                logger.info(f"FLUX generation successful: {response.get('count', 0)} images")
                logger.info(f"Cost: ${response.get('cost_usd', 0):.6f}")
                logger.info(f"URL: {response.get('url', 'N/A')}")
                
                return {
                    "status": "success",
                    "result": response,
                    "metadata": result.get("metadata", {})
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"FLUX generation failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"FLUX generation failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_flux_kontext_image_to_image(self) -> Dict[str, Any]:
        """Test FLUX Kontext Pro image-to-image generation"""
        logger.info("Testing FLUX Kontext Pro image-to-image...")
        
        try:
            config = self.test_configs["flux_kontext"]
            
            result = await self.client.invoke(
                input_data=config["prompt"],
                task=config["task"],
                service_type="image",
                model=config["model"],
                provider=config["provider"],
                init_image=config["init_image"],
                strength=0.8
            )
            
            if result.get("success"):
                response = result["result"]
                logger.info(f"FLUX Kontext generation successful: {response.get('count', 0)} images")
                logger.info(f"Cost: ${response.get('cost_usd', 0):.6f}")
                logger.info(f"URL: {response.get('url', 'N/A')}")
                
                return {
                    "status": "success",
                    "result": response,
                    "metadata": result.get("metadata", {})
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"FLUX Kontext generation failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"FLUX Kontext generation failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_sticker_generation(self) -> Dict[str, Any]:
        """Test sticker generation"""
        logger.info("Testing Sticker Maker...")
        
        try:
            config = self.test_configs["sticker_maker"]
            
            result = await self.client.invoke(
                input_data=config["prompt"],
                task=config["task"],
                service_type="image",
                model=config["model"],
                provider=config["provider"],
                steps=17,
                width=1152,
                height=1152,
                output_format="webp",
                output_quality=100
            )
            
            if result.get("success"):
                response = result["result"]
                logger.info(f"Sticker generation successful: {response.get('count', 0)} stickers")
                logger.info(f"Cost: ${response.get('cost_usd', 0):.6f}")
                logger.info(f"URL: {response.get('url', 'N/A')}")
                
                return {
                    "status": "success",
                    "result": response,
                    "metadata": result.get("metadata", {})
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Sticker generation failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"Sticker generation failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_face_swap(self) -> Dict[str, Any]:
        """Test face swap"""
        logger.info("Testing Face Swap...")
        
        try:
            config = self.test_configs["face_swap"]
            
            result = await self.client.invoke(
                input_data=config["swap_image"],  # Use swap_image as input_data
                task=config["task"],
                service_type="image",
                model=config["model"],
                provider=config["provider"],
                target_image=config["target_image"],
                hair_source="target",
                user_gender="default",
                user_b_gender="default"
            )
            
            if result.get("success"):
                response = result["result"]
                logger.info(f"Face swap successful: {response.get('count', 0)} images")
                logger.info(f"Cost: ${response.get('cost_usd', 0):.6f}")
                logger.info(f"URL: {response.get('url', 'N/A')}")
                
                return {
                    "status": "success",
                    "result": response,
                    "metadata": result.get("metadata", {})
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Face swap failed: {error_msg}")
                return {"status": "error", "error": error_msg}
                
        except Exception as e:
            logger.error(f"Face swap failed with exception: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Test all image generation services"""
        logger.info("Starting comprehensive image generation tests using ISA Model Client...")
        
        results = {}
        
        # Test each service
        tests = [
            ("flux_text_to_image", self.test_flux_text_to_image),
            ("flux_image_to_image", self.test_flux_kontext_image_to_image),
            ("sticker_generation", self.test_sticker_generation),
            ("face_swap", self.test_face_swap)
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
    tester = ImageGenerationTester()
    
    # Get service health
    logger.info("Checking service health...")
    health = await tester.get_service_health()
    logger.info(f"Service health: {health}")
    
    # Run all tests
    results = await tester.test_all_services()
    
    # Calculate total cost
    total_cost = 0.0
    for test_name, result in results.items():
        if result.get("status") == "success":
            cost = result.get("result", {}).get("cost_usd", 0.0)
            total_cost += cost
    
    logger.info(f"\nTotal cost for all tests: ${total_cost:.6f}")
    
    return results

if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())