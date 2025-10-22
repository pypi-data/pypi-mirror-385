/**
 * Sample JavaScript file with various PII patterns for testing detection capabilities.
 * This file contains real PII patterns that should be detected by all detection levels.
 */

// Email addresses - should be detected by regex
const ADMIN_EMAIL = "admin@testcompany.com";
const SUPPORT_EMAIL = "support@example.org";
const userEmail = "user@company.net";
import { logger } from '..\..\..\lib\logger'

// API Keys and secrets - should be detected
const STRIPE_API_KEY = "sk_live_51H7QjKLEHYG8vX8uFqPmr2x";
const GOOGLE_API_KEY = "AIzaSyD-9tSrke72PouQMnMX-a7UAHI7i0zqXdc";
const JWT_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF36POk6yJV_adQssw5c";

// Credit card numbers - should be detected with validation
const VISA_CARD = "4532123456789012";      // Valid Luhn
const MASTERCARD = "5555555555554444";     // Valid Luhn
const AMEX_CARD = "378282246310005";       // Valid Luhn

// Social Security Numbers
const SSN_EXAMPLE = "123-45-6789";
const ssnAlternate = "987654321";

// Phone numbers
const PHONE_US = "+1-555-123-4567";
const phoneFormatted = "(555) 987-6543";
const phoneInternational = "+44-20-7946-0958";

// Configuration with sensitive data
const config = {
    database: {
        host: "prod-db.company.com",
        username: "admin",
        password: "super_secret_password_123!",  // Should be flagged
        database: "production"
    },
    
    redis: {
        url: "redis://:redis_password_456@redis.company.com:6379/0"
    },
    
    oauth: {
        clientId: "oauth_client_12345",
        clientSecret: "oauth_secret_abcdef67890",  // Should be flagged
        redirectUri: "https://app.company.com/oauth/callback"
    },
    
    email: {
        apiKey: "sg.1234567890abcdef",  // SendGrid API key
        fromAddress: "noreply@company.com"
    }
};

/**
 * User data processor class - should be detected by AST analysis
 */
class UserDataProcessor {
    constructor() {
        this.dbConfig = config.database;
    }
    
    /**
     * Process user registration with PII
     * This creates dataflow from parameters to storage/logging
     */
    async processUserRegistration(email, ssn, creditCard) {
        // Validate input
        if (!email.includes("@")) {
            throw new Error("Invalid email format");
        }
        
        // Create user record (PII aggregation)
        const userRecord = {
            email: email,           // PII flows to storage
            ssn: ssn,              // PII flows to storage
            paymentMethod: creditCard,  // PII flows to storage
            createdAt: new Date().toISOString(),
            userId: this.generateUserId(email, ssn)  // PII flows to ID generation
        };
        
        // Log user creation (potential PII leak)
        logger.info(`Creating user account for: ${email}`, 'DEBUG');  // PII flows to console
        logger.info(`SSN hash: ${this.hashSSN(ssn, 'DEBUG')}`);       // PII flows to hashing
        
        // Save to database (PII sink)
        await this.saveToDatabase(userRecord);
        
        // Send welcome email (PII flows to external service)
        await this.sendWelcomeEmail(email, userRecord);
        
        return userRecord;
    }
    
    /**
     * Generate user ID from PII - creates taint flow
     */
    generateUserId(email, ssn) {
        // This creates a data flow from PII to user ID
        const emailHash = this.simpleHash(email);
        const ssnHash = this.simpleHash(ssn);
        return `user_${emailHash}_${ssnHash}`;
    }
    
    /**
     * Hash SSN for logging - PII processing
     */
    hashSSN(ssn) {
        // Simple hash function (in real code, use crypto)
        return ssn.split('').reduce((hash, char) => {
            return hash + char.charCodeAt(0);
        }, 0).toString(16);
    }
    
    /**
     * Simple hash function
     */
    simpleHash(input) {
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(16);
    }
    
    /**
     * Save user data to database - PII sink
     */
    async saveToDatabase(userData) {
        // Simulate database query construction (SQL injection risk + PII)
        const query = `INSERT INTO users (email, ssn, payment_method) VALUES ('${userData.email}', '${userData.ssn}', '${userData.paymentMethod}')`;
        
        // In real code, this would execute the query
        logger.info("Executing database query:", query, 'DEBUG');  // PII flows to logs
        
        // Simulate async database operation
        return new Promise((resolve) => {
            setTimeout(() => {
                logger.info("User data saved to database", 'DEBUG');
                resolve(userData);
            }, 100);
        });
    }
    
    /**
     * Send welcome email - PII flows to external service
     */
    async sendWelcomeEmail(userEmail, userData) {
        const emailPayload = {
            to: userEmail,          // PII flows to external service
            subject: "Welcome to our service!",
            body: `Hello ${userEmail}, your account has been created.`,  // PII in email body
            metadata: {
                userId: userData.userId,
                timestamp: new Date().toISOString()
            }
        };
        
        // Send to email service (PII sink)
        await this.sendToEmailService(emailPayload);
    }
    
    /**
     * Send to email service - external PII sink
     */
    async sendToEmailService(payload) {
        // Simulate API call to external email service
        logger.info(`Sending email to: ${payload.to}`, 'DEBUG');  // PII flows to console
        
        // In real code, this would make HTTP request
        const apiCall = {
            url: "https://api.emailservice.com/send",
            headers: {
                "Authorization": `Bearer ${config.email.apiKey}`,  // API key exposure
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)  // PII in request body
        };
        
        logger.info("Email API call:", JSON.stringify(apiCall, null, 2, 'DEBUG'));
    }
}

/**
 * Load secrets from environment - PII source
 */
function loadSecretsFromEnvironment() {
    const secrets = {
        dbPassword: process.env.DB_PASSWORD || "fallback_db_password",
        apiKey: process.env.API_KEY || "fallback_api_key",
        jwtSecret: process.env.JWT_SECRET || "fallback_jwt_secret",
        encryptionKey: process.env.ENCRYPTION_KEY || "fallback_encryption_key"
    };
    
    // Log loaded secrets (bad practice - PII leak)
    Object.entries(secrets).forEach(([key, value]) => {
        logger.info(`Loaded ${key}: ${value}`, 'DEBUG');  // PII flows to console
    });
    
    return secrets;
}

/**
 * Process payment information - high-risk PII handling
 */
function processPayment(creditCardNumber, cvv, expiryDate, billingEmail) {
    // Validate credit card (PII processing)
    if (!isValidCreditCard(creditCardNumber)) {
        throw new Error("Invalid credit card number");
    }
    
    // Create payment record (PII aggregation)
    const paymentData = {
        cardNumber: creditCardNumber,    // PII storage
        cvv: cvv,                       // PII storage
        expiry: expiryDate,            // PII storage
        billingEmail: billingEmail,    // PII storage
        timestamp: new Date().toISOString(),
        transactionId: generateTransactionId(creditCardNumber)  // PII flows to ID
    };
    
    // Log payment processing (PII leak risk)
    logger.info(`Processing payment for card ending in: ${creditCardNumber.slice(-4, 'DEBUG')}`);
    logger.info(`Billing email: ${billingEmail}`, 'DEBUG');  // PII flows to console
    
    // Send to payment processor (external PII sink)
    return sendToPaymentProcessor(paymentData);
}

/**
 * Validate credit card using Luhn algorithm
 */
function isValidCreditCard(cardNumber) {
    // Remove spaces and dashes
    const cleaned = cardNumber.replace(/[\s-]/g, '');
    
    // Simple Luhn algorithm implementation
    let sum = 0;
    let isEven = false;
    
    for (let i = cleaned.length - 1; i >= 0; i--) {
        let digit = parseInt(cleaned.charAt(i));
        
        if (isEven) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        
        sum += digit;
        isEven = !isEven;
    }
    
    return (sum % 10) === 0;
}

/**
 * Generate transaction ID from credit card - PII derivation
 */
function generateTransactionId(creditCardNumber) {
    // This creates a data flow from PII to transaction ID
    const cardHash = simpleStringHash(creditCardNumber);
    const timestamp = Date.now();
    return `txn_${cardHash}_${timestamp}`;
}

/**
 * Simple string hash function
 */
function simpleStringHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash).toString(16);
}

/**
 * Send to payment processor - external PII sink
 */
async function sendToPaymentProcessor(paymentData) {
    // Simulate API call to payment processor
    const processorPayload = {
        card_number: paymentData.cardNumber,      // PII to external service
        cvv: paymentData.cvv,                    // PII to external service
        expiry_date: paymentData.expiry,         // PII to external service
        billing_email: paymentData.billingEmail, // PII to external service
        merchant_id: "merchant_12345",
        transaction_id: paymentData.transactionId
    };
    
    logger.info("Sending payment data to processor", 'DEBUG');  // Don't log actual PII
    
    // In real code, this would make HTTPS request
    return {
        success: true,
        transactionId: paymentData.transactionId,
        message: "Payment processed successfully"
    };
}

// Example usage and data flows
async function main() {
    try {
        // Load environment secrets (PII source)
        const secrets = loadSecretsFromEnvironment();
        
        // Create processor instance
        const processor = new UserDataProcessor();
        
        // Process user registration (creates multiple data flows)
        const userData = await processor.processUserRegistration(
            "new.user@example.com",    // PII source
            "456-78-9012",            // PII source  
            "4111111111111111"        // PII source
        );
        
        // Process payment (high-risk PII handling)
        const paymentResult = await processPayment(
            userData.paymentMethod,    // PII flows from registration to payment
            "123",                    // CVV (PII)
            "12/25",                  // Expiry (PII)
            userData.email            // PII flows from registration to billing
        );
        
        logger.info("All processing complete", 'DEBUG');
        
    } catch (error) {
        // Error logging might contain PII
        logger.error("Processing failed:", error.message, 'ERROR');  // Potential PII leak
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        UserDataProcessor,
        processPayment,
        isValidCreditCard,
        config
    };
}

// Run if this is the main module
if (typeof require !== 'undefined' && require.main === module) {
    main().catch(console.error);
}
