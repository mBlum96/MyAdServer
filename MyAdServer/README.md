- [AdSelectionView API](#adselectionview-api)
  - [Functionality](#functionality)
  - [API Endpoint](#api-endpoint)
    - [Data Requirements](#data-requirements)
  - [Response](#response)
  - [Error Handling](#error-handling)
  - [Adding New Broadcasting Policies](#adding-new-broadcasting-policies)
- [Reward Update API](#reward-update-api)
  - [Functionality](#functionality-1)
  - [API Endpoint](#api-endpoint-1)
    - [Data Requirements](#data-requirements-1)
  - [Response](#response-1)
  - [Security Measures](#security-measures)
    - [Admin-only access](#admin-only-access)
    - [CSRF Protection](#csrf-protection)
  - [Error Handling](#error-handling-1)
- [Reward Accumulation API](#reward-accumulation-api)
  - [Functionality](#functionality-2)
  - [API Endpoint](#api-endpoint-2)
    - [Data Requirements](#data-requirements-2)
  - [Response](#response-2)
  - [Security Measures](#security-measures-1)
    - [One-Time SSL Token](#one-time-ssl-token)
    - [Future Considerations](#future-considerations)
  - [Handling Performance Issues](#handling-performance-issues)
    - [Caching Strategies](#caching-strategies)
    - [Database Indexing](#database-indexing)
    - [Query Optimization](#query-optimization)
  - [Error Handling](#error-handling-2)
- [Reward Deduction API](#reward-deduction-api)
  - [Functionality](#functionality-3)
  - [API Endpoint](#api-endpoint-3)
    - [Data Requirements](#data-requirements-3)
  - [Response](#response-3)
  - [Error Handling](#error-handling-3)
- [Reward History API](#reward-history-api)
  - [Functionality](#functionality-4)
  - [API Endpoint](#api-endpoint-4)
    - [Data Requirements](#data-requirements-4)
  - [Response](#response-4)
  - [Error Handling](#error-handling-4)
- [Reward Balance API](#reward-balance-api)
  - [Functionality](#functionality-5)
  - [API Endpoint](#api-endpoint-5)
    - [Data Requirements](#data-requirements-5)
  - [Response](#response-5)
  - [Error Handling](#error-handling-5)
- [Adding New Ad Broadcasting Policies](#adding-new-ad-broadcasting-policies-1)
  - [Overview](#overview)
  - [Steps to Add a New Policy](#steps-to-add-a-new-policy)
    - [Step 1: Define the New Policy](#step-1-define-the-new-policy)
    - [Step 2: Implement policy logic](#step-2-implement-policy-logic)
    - [Step 3: Update select_ads method](#step-3-update-select_ads-method)
- [Handling Performance Issues](#handling-performance-issues-1)
  - [Caching Strategies](#caching-strategies-1)
  - [Database Indexing](#database-indexing-1)
  - [Query Optimization](#query-optimization-1)
- [Security Measures](#security-measures-2)
  - [For accumulating rewards](#for-accumulating-rewards)
    - [One-Time SSL Token](#one-time-ssl-token-1)
  - [For setting reward value](#for-setting-reward-value)
    - [Admin-only access](#admin-only-access-1)
    - [CSRF Protection](#csrf-protection-1)

# AdSelectionView API

## Functionality

Handles the selection and delivery of ads.
Generates a secure token for each ad for validating user interactions.

## API Endpoint

URL: /get-ads/
Method: GET

### Data Requirements:

user_id: ID of the user we need to select ads for.
gender: Gender of the user we need to select ads for.
country: Country of the user we need to select ads for.

## Response

Success: A list of ads with their details and a unique token for each ad.
Failure: A message indicating no ads are available.

## Error Handling

Returns a 404 status code if no suitable ads are found for the user's criteria.
Returns a 500 status code for internal server errors.

## Adding New Broadcasting Policies

Define new policy in constants.py.
Implement selection logic in a method like select_using_new_policy in the
AdSelectionView class.
Update select_ads method in the AdSelectionView to include the new policy.

# Reward Update API

## Functionality:

Allows admin users to update the reward value for an ad.

## API Endpoint

URL: /reward-update/
Method: POST

### Data Requirements:

ad_id: ID of the ad that was interacted with.
reward: The reward amount we want to set for interacting with the ad.

## Security Measures

### Admin-only access

using @method_decorator(user_passes_test(lambda u: u.is_staff)).

### CSRF Protection

Django's built-in CSRF protection is enabled for this API.
A CSRF token must be included in POST requests to prevent Cross-Site Request Forgery attacks.
Admin-Only Access for Reward Updates
The API uses the user_passes_test decorator to ensure that only admin users can update reward values.
This is a crucial measure to prevent unauthorized manipulation of reward values.

## Response

Success: A confirmation message indicating the reward has been updated.
Failure: A message indicating the reason for the failure (e.g., ad not found, invalid data).

## Error Handling

Returns a 400 status code for invalid requests (bad JSON, missing fields, invalid reward values).
Returns a 404 status code if the specified ad is not found.
Returns a 500 status code for unexpected server errors.

# Reward Accumulation API

## Functionality

Validates the interaction using a secure, one-time token and credits the user's
account with the corresponding reward.

## API Endpoint

URL: /accumulate-reward/
Method: POST

### Data Requirements:

user_id: ID of the user who interacted with the ad.
ad_id: ID of the ad that was interacted with.
reward: The reward amount for interacting with the ad.
token: A unique, one-time use token associated with the ad view.

## Response

Success: Returns a message confirming the reward accumulation.
Failure: Returns an error message, typically when the token is invalid or already used.

## Security Measures

### One-Time SSL Token

Each ad interaction is secured with a one-time SSL token generated in the AdSelection process.
This token must be sent back with the reward accumulation request, ensuring that rewards can only be claimed through legitimate ad interactions.
Once used, the token is marked as such in the database, preventing reuse.

### Future Considerations

REST API Implementation: For enhanced decoupling and security, a RESTful API structure can be considered. This would require additional development time but offers benefits in terms of standardization and scalability.
Private Reward Field: To further tighten security, the reward field could be made private with a dedicated admin-accessible method for updates.

## Handling Performance Issues

### Caching Strategies

Caching is implemented to minimize database queries, especially for data that remains relatively stable.
This reduces server response times and lightens database load, crucial for high-traffic scenarios.

### Database Indexing

Indexes in the PostgreSQL database are used to speed up data retrieval, especially for frequently queried fields like target_country and target_gender in the Ad model.

### Query Optimization

Django’s select_related and prefetch_related are used for efficient handling of related objects.
This is particularly beneficial when dealing with a large number of Ad objects and their associated data.

## Error Handling

Returns a 400 status code for invalid tokens or if required fields are missing.
Returns a 404 status code if the user or ad is not found.
Returns a 500 status code for unexpected server errors.

# Reward Deduction API

This API deducts a specified amount of reward from a user's account.

## Functionality

Deducts rewards from a user's balance.
Ensures the reward balance does not go negative.

## API Endpoint

URL: /reward-deduction/
Method: POST

### Data Requirements:

user_id: ID of the user who's reward balance we want to reduce.
amount: The amount to be reduced from the account.

## Response

Success: A confirmation message indicating the reward has been updated (deducted).
Failure: A message indicating the reason for the failure (e.g., ad not found, invalid data).

## Error Handling

400: Invalid data or insufficient balance.
404: User not found.
500: Unexpected server errors.

# Reward History API

## Functionality

Fetches the user's reward transactions for the last week.

## API Endpoint

URL: /reward-history/
Method: GET

### Data Requirements

user_id: ID of the user we want to get the history of.

## Response

Success: A list of reward transactions for the last week.
Failure: A message indicating the reason for the failure (e.g., ad not found, invalid data).

## Error Handling

Returns a 400 status code if the user ID is missing from the request.
Returns a 404 status code if the user is not found.
Returns a 500 status code for unexpected server errors.

# Reward Balance API

## Functionality

Displays the total reward balance of a user.

## Endpoint

URL: /reward-balance/
Method: GET

### Data Requirements

user_id: ID of the user who's balance we want to get.

## Response

Success: The total balance of the user.
Failure: A message indicating the reason for the failure (e.g., ad not found, invalid data).

## Error Handling

Returns a 400 status code if the user ID is missing from the request.
Returns a 404 status code if the user is not found.
Returns a 500 status code for unexpected server errors.

# Adding New Ad Broadcasting Policies

## Overview

This section guides you through the process of adding new ad broadcasting policies to the AdSelectionView.

## Steps to Add a New Policy

### Step 1: Define the New Policy

Add a new policy constant in `constants.py`.
Example:

```python
GROUP_NEW_POLICY = 4  # Adjust the number based on existing policies
```

### Step 2: Implement policy logic

Create a new method select_using_new_policy that contains the logic for the new policy.
Example:

```python
def select_using_new_policy(self, ads, max_ads):
    # Implement your custom logic here
    pass
```

### Step 3: Update select_ads method

Example:

```python
def select_ads(self, ads):
    # existing policies...
    if self.user_group == GROUP_NEW_POLICY:
        return self.select_using_new_policy(ads, MAX_ADS_SHOWN)
    # other conditions...

```

# Handling Performance Issues

## Caching Strategies

Caching is implemented to minimize database queries, especially for data that remains relatively stable.
This reduces server response times and lightens database load, crucial for high-traffic scenarios.

## Database Indexing

Indexes in the PostgreSQL database are used to speed up data retrieval, especially for frequently queried fields like target_country and target_gender in the Ad model.

## Query Optimization

Django’s select_related and prefetch_related are used for efficient handling of related objects.
This is particularly beneficial when dealing with a large number of Ad objects and their associated data.

# Security Measures

## For accumulating rewards:

### One-Time SSL Token

Each ad interaction is secured with a one-time SSL token generated in the AdSelection process.
This token must be sent back with the reward accumulation request, ensuring that rewards can only be claimed through legitimate ad interactions.
Once used, the token is marked as such in the database, preventing reuse.

## For setting reward value:

### Admin-only access

using

```python
@method_decorator(user_passes_test(lambda u: u.is_staff))
```

To protect from users who do not posses admin priviledges.

### CSRF Protection

Django's built-in CSRF protection is enabled for this API.
A CSRF token must be included in POST requests to prevent Cross-Site Request Forgery attacks.
Admin-Only Access for Reward Updates
The API uses the user_passes_test decorator to ensure that only admin users can update reward values.
This is a crucial measure to prevent unauthorized manipulation of reward values.
