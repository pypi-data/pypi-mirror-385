# API Endpoint Mapping

This document maps the current SDK endpoints to new RESTful API endpoints following the [Zalando RESTful API Guidelines](https://opensource.zalando.com/restful-api-guidelines/) and our internal API guidelines.

## Mapping Table

| HTTP Method                  | New HTTP Method | Current Endpoint                                           | New Endpoint                                                   | Responsible |
|------------------------------|-----------------|------------------------------------------------------------|----------------------------------------------------------------|-------------|
| **Core Service**             |                 | https://core.basalam.com                                   |                                                                | @remo       |
| POST                         | POST            | /v3/users/{user_id}/vendors                                | /v1/users/{user_id}/vendors                                    |             |
| PATCH                        | PATCH           | /v3/vendors/{vendor_id}                                    | /v1/vendors/{vendor_id}                                        |             |
| GET                          | GET             | /v3/vendors/{vendor_id}                                    | /v1/vendors/{vendor_id}                                        |             |
| GET                          | GET             | /v3/shipping-methods/defaults                              | /v1/shipping-methods/defaults                                  |             |
| GET                          | GET             | /v3/shipping-methods                                       | /v1/shipping-methods                                           |             |
| GET                          | GET             | /v3/vendors/{vendor_id}/shipping-methods                   | /v1/vendors/{vendor_id}/shipping-methods                       |             |
| PUT                          | PUT             | /v3/vendors/{vendor_id}/shipping-methods                   | /v1/vendors/{vendor_id}/shipping-methods                       |             |
| GET                          | GET             | /v3/vendors/{vendor_id}/products                           | /v1/vendors/{vendor_id}/products                               |             |
| PATCH                        | PATCH           | /v3/vendors/{vendor_id}/status                             | /v1/vendors/{vendor_id}/status                                 |             |
| POST                         | POST            | /v3/vendors/{vendor_id}/change-mobile-request              | /v1/vendors/{vendor_id}/mobile-change-requests                 |             |
| POST                         | POST            | /v3/vendors/{vendor_id}/change-mobile-confirm              | /v1/vendors/{vendor_id}/mobile-change-confirmations            |             |
| POST                         | POST            | /v4/vendors/{vendor_id}/products                           | /v1/vendors/{vendor_id}/products                               |             |
| PATCH                        | PATCH           | /v4/vendors/{vendor_id}/products                           | /v1/vendors/{vendor_id}/products/batch-updates                 |             |
| PATCH                        | PATCH           | /v4/products/{product_id}                                  | /v1/products/{product_id}                                      |             |
| GET                          | GET             | /v4/products/{product_id}                                  | /v1/products/{product_id}                                      |             |
| GET                          | GET             | /v3/products                                               | /v1/products                                                   |             |
| POST                         | POST            | /v4/vendors/{vendor_id}/bulk-update-product-request        | /v1/vendors/{vendor_id}/batch-jobs                             |             |
| PATCH                        | PATCH           | /v4/products/{product_id}/variations/{variation_id}        | /v1/products/{product_id}/variations/{variation_id}            |             |
| GET                          | GET             | /v3/vendors/{vendor_id}/bulk-update-product-request        | /v1/vendors/{vendor_id}/batch-jobs                             |             |
| GET                          | GET             | /v3/vendors/{vendor_id}/bulk-update-product-request/count  | /v1/vendors/{vendor_id}/batch-jobs/count                       |             |
| GET                          | GET             | /v3/bulk-update-product-request/{id}/unsuccessful_products | /v1/batch-jobs/{job_id}/failed-items                           |             |
| GET                          | GET             | /v3/products/{product_id}/shelves                          | /v1/products/{product_id}/shelves                              |             |
| POST                         | POST            | /v3/vendors/{vendor_id}/discounts                          | /v1/vendors/{vendor_id}/discounts                              |             |
| DELETE                       | DELETE          | /v3/vendors/{vendor_id}/discounts                          | /v1/vendors/{vendor_id}/discounts                              |             |
| GET                          | GET             | /v3/users/me                                               | /v1/users/me                                                   |             |
| POST                         | POST            | /v3/users/{user_id}/confirm-mobile-request                 | /v1/users/{user_id}/mobile-verification-requests               |             |
| POST                         | POST            | /v3/users/{user_id}/confirm-mobile                         | /v1/users/{user_id}/mobile-verification-confirmations          |             |
| POST                         | POST            | /v3/users/{user_id}/change-mobile-request                  | /v1/users/{user_id}/mobile-change-requests                     |             |
| POST                         | POST            | /v3/users/{user_id}/change-mobile-confirm                  | /v1/users/{user_id}/mobile-change-confirmations                |             |
| GET                          | GET             | /v3/users/{user_id}/bank-information                       | /v1/users/{user_id}/bank-accounts                              |             |
| POST                         | POST            | /v3/users/{user_id}/bank-information                       | /v1/users/{user_id}/bank-accounts                              |             |
| POST                         | POST            | /v3/users/{user_id}/bank-information/verify-otp            | /v1/users/{user_id}/bank-accounts/verify-otp                   |             |
| POST                         | POST            | /v3/users/{user_id}/bank-information/verify                | /v1/users/{user_id}/bank-accounts/verify                       |             |
| DELETE                       | DELETE          | /v3/users/{user_id}/bank-information/{bank_account_id}     | /v1/users/{user_id}/bank-accounts/{bank_account_id}            |             |
| PATCH                        | PATCH           | /v3/bank-information/{bank_account_id}                     | /v1/users/{user_id}/bank-accounts/{bank_account_id}            |             |
| PATCH                        | PATCH           | /v3/users/{user_id}/verification-request                   | /v1/users/{user_id}/verification-requests                      |             |
| GET                          | GET             | /v3/categories/{category_id}/attributes                    | /v1/categories/{category_id}/attributes                        |             |
| GET                          | GET             | /v3/categories                                             | /v1/categories                                                 |             |
| GET                          | GET             | /v3/categories/{category_id}                               | /v1/categories/{category_id}                                   |             |
| **Chat Service**             |                 | https://conversation.basalam.com                           |                                                                | @a.ehsani   |
| POST                         | POST            | /v3/messages                                               | /v1/chats/{chat_id}/messages                                   |             |
| POST                         | POST            | /v3/chats                                                  | /v1/chats                                                      |             |
| GET                          | GET             | /v3/messages                                               | /v1/chats/{chat_id}/messages                                   |             |
| GET                          | GET             | /v3/chats                                                  | /v1/chats                                                      |             |
| **Order Service**            |                 | https://order.basalam.com                                  |                                                                |             |
| GET                          | GET             | /v2/basket                                                 | /v1/baskets                                                    |             |
| GET                          | GET             | /v2/basket/product/{product_id}/status                     | /v1/baskets/products/{product_id}/status                       |             |
| POST                         | POST            | /v2/invoice/{invoice_id}/payment                           | /v1/invoices/{invoice_id}/payments                             |             |
| GET                          | GET             | /v2/invoice/payable                                        | /v1/invoices/payable                                           |             |
| GET                          | GET             | /v2/invoice/unpaid                                         | /v1/invoices/unpaid                                            |             |
| GET                          | GET             | /v2/payment/{pay_id}/callback                              | /v1/payments/{payment_id}/callbacks                            |             |
| POST                         | POST            | /v2/payment/{pay_id}/callback                              | /v1/payments/{payment_id}/callbacks                            |             |
| **Order Processing Service** |                 | https://order-processing.basalam.com                       |                                                                |             |
| GET                          | GET             | /v3/customer-orders                                        | /v1/customer-orders                                            |             |
| GET                          | GET             | /v3/customer-orders/{order_id}                             | /v1/customer-orders/{order_id}                                 |             |
| GET                          | GET             | /v3/customer-items                                         | /v1/customer-orders/items                                      |             |
| GET                          | GET             | /v3/customer-items/{item_id}                               | /v1/customer-orders/items/{item_id}                            |             |
| GET                          | GET             | /v3/vendor-parcels                                         | /v1/vendor-parcels                                             |             |
| GET                          | GET             | /v3/vendor-parcels/{parcel_id}                             | /v1/vendor-parcels/{parcel_id}                                 |             |
| GET                          | GET             | /v3/orders-calculate-stats                                 | /v1/orders/stats                                               |             |
| **Wallet Service**           |                 |                                                            |                                                                |             |
| POST                         | POST            | /v2/user/{user_id}/balance                                 | /v1/users/{user_id}/balance                                    |             |
| GET                          | GET             | /v2/user/{user_id}/history                                 | /v1/users/{user_id}/transactions                               |             |
| POST                         | POST            | /v2/user/{user_id}/spend                                   | /v1/users/{user_id}/expenses                                   |             |
| POST                         | POST            | /v2/user/{user_id}/credit/{credit_id}/spend                | /v1/users/{user_id}/credits/{credit_id}/transactions           |             |
| GET                          | GET             | /v2/user/{user_id}/spend/{spend_id}                        | /v1/users/{user_id}/expenses/{expense_id}                      |             |
| DELETE                       | DELETE          | /v2/user/{user_id}/spend/{spend_id}                        | /v1/users/{user_id}/expenses/{expense_id}                      |             |
| GET                          | GET             | /v2/user/{user_id}/spend/by-ref/{reason_id}/{reference_id} | /v1/users/{user_id}/expenses/by-ref/{reason_id}/{reference_id} |             |
| DELETE                       | DELETE          | /v2/user/{user_id}/spend/by-ref/{reason_id}/{reference_id} | /v1/users/{user_id}/expenses/by-ref/{reason_id}/{reference_id} |             |
| POST                         | POST            | /v2/refund                                                 | /v1/refunds                                                    |             |
| POST                         | POST            | /v2/can-rollback-refund                                    | /v1/refunds/{refund_id}/can-rollback                           |             |
| DELETE                       | DELETE          | /v2/rollback-refund                                        | /v1/refunds/{refund_id}/rollbacks                              |             |
| **Search Service**           |                 | https://search.basalam.com                                 |                                                                | @a.araste   |
| POST                         | POST            | /ai-engine/api/v2.0/product/search                         | /v1/products/search                                            |             |
| **Upload Service**           |                 | https://uploadio.basalam.com                               |                                                                |             |
| POST                         | POST            | /v3/files                                                  | /v1/files                                                      |             |
| **Webhook Service**          |                 | https://webhook.basalam.com                                |                                                                |             |
| GET                          | GET             | /v1/services                                               | /v1/webhooks/services                                          |             |
| POST                         | POST            | /v1/services                                               | /v1/webhooks/services                                          |             |
| GET                          | GET             | /v1/webhooks                                               | /v1/webhooks                                                   |             |
| POST                         | POST            | /v1/webhooks                                               | /v1/webhooks                                                   |             |
| PATCH                        | PATCH           | /v1/webhooks/{webhook_id}                                  | /v1/webhooks/{webhook_id}                                      |             |
| DELETE                       | DELETE          | /v1/webhooks/{webhook_id}                                  | /v1/webhooks/{webhook_id}                                      |             |
| GET                          | GET             | /v1/webhooks/events                                        | /v1/webhooks/events                                            |             |
| GET                          | GET             | /v1/webhooks/customers                                     | /v1/webhooks/customers                                         |             |
| GET                          | GET             | /v1/webhooks/{webhook_id}/logs                             | /v1/webhooks/{webhook_id}/logs                                 |             |
| POST                         | POST            | /v1/customers/webhooks                                     | /v1/customers/webhooks                                         |             |
| DELETE                       | DELETE          | /v1/customers/webhooks                                     | /v1/customers/webhooks                                         |             |
| GET                          | GET             | /v1/customers/webhooks                                     | /v1/customers/webhooks                                         |             |
## Key Changes Applied

1. **Uniform Base URL**: All endpoints now use `gateway.basalam.com/v1` as the base URL
2. **Added API Version Prefix**: Added `/v1` prefix to all URLs for future versioning needs
3. **Used Plural Resource Names**: All resource names are now pluralized (e.g., `user` → `users`)
4. **Used Kebab-Case for Multi-Word Resources**: For example, `webhook-services`, `order-items`, `tracking-info`
5. **Consistent Resource Hierarchy**: Limited resource nesting to maintain clean URLs
6. **Replaced Verbs with Nouns**: Changed action verbs to noun resources (e.g., `cancel` → `cancellations`, `rollback` → `rollbacks`)
7. **Added Prefixes for Related Resources**: For example, `order-items` instead of just `items` to clarify domain
8. **Standardized Resource Access Patterns**:
   - `/resources` for collection resources
   - `/resources/{resource_id}` for specific resources
   - `/resources/{resource_id}/sub-resources` for sub-resources

## Implementation Notes

1. **URL Versioning Note**: While the Zalando guidelines recommend media type versioning over URL versioning, we've included URL versioning (`/v1`) for compatibility reasons and to provide a clear upgrade path for future versions. In a strict interpretation of the guidelines, this would be implemented using media type versioning:
   ```
   Accept: application/vnd.basalam.v1+json
   ```

2. **Query Parameters**: Following Zalando guidelines, query parameters should use snake_case:
   ```
   /orders?sort=created_at,desc&filter=status:pending&page_size=25
   ```
