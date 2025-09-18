import google.genai as genai
from google.genai import types
from PIL import Image
from io import BytesIO

# client = genai.Client()
client = genai.Client(api_key="")

# Base image prompt: "A photorealistic, high-resolution photograph of a busy city street in New York at night, with bright neon signs, yellow taxis, and tall skyscrapers."
city_image = Image.open('IMG_8495.JPG')
text_input = """Transform the provided photograph of a man in mountain into the artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original composition of trees and rocks, but render all elements with swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows."""

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[city_image, text_input],
)

image_parts = [
    part.inline_data.data
    for part in response.candidates[0].content.parts
    if part.inline_data
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save(f"{city_image.split('.')[0]}_generated.{city_image.split('.')[1]}")
    image.show()


"""
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: ' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
"""

"""
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED.
{
    'error': {
        'code': 429,
        'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.\n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0\n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0\n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0\nPlease retry in 6.012022533s.',
        'status': 'RESOURCE_EXHAUSTED',
        'details': [
            {
                '@type': 'type.googleapis.com/google.rpc.QuotaFailure',
                'violations': [
                    {
                        'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_input_token_count',
                        'quotaId': 'GenerateContentInputTokensPerModelPerMinute-FreeTier',
                        'quotaDimensions': {
                            'location': 'global',
                            'model': 'gemini-2.5-flash-preview-image'
                        }
                    },
                    {
                        'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests',
                        'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier',
                        'quotaDimensions': {
                            'location': 'global',
                            'model': 'gemini-2.5-flash-preview-image'
                        }
                    },
                    {
                        'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests',
                        'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier',
                        'quotaDimensions': {
                            'location': 'global',
                            'model': 'gemini-2.5-flash-preview-image'
                        }
                    }
                ]
            },
            {
                '@type': 'type.googleapis.com/google.rpc.Help',
                'links': [
                    {
                        'description': 'Learn more about Gemini API quotas',
                        'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'
                    }
                ]
            },
            {
                '@type': 'type.googleapis.com/google.rpc.RetryInfo',
                'retryDelay': '6s'
            }
        ]
    }
}
"""