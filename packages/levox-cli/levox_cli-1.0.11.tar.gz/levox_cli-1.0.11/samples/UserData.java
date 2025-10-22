package com.example.userdata;

import java.util.List;
import java.util.ArrayList;
import java.time.LocalDateTime;

/**
 * User data management class for handling PII information
 * This is a sample file to test the Java parser integration
 */
public class UserData {
    
    // User personal information
    private String firstName;
    private String lastName;
    private String emailAddress;
    private String phoneNumber;
    private String socialSecurityNumber;
    private String dateOfBirth;
    private String homeAddress;
    private String zipCode;
    
    // Configuration constants
    private static final String DEFAULT_EMAIL_DOMAIN = "example.com";
    private static final String API_ENDPOINT = "https://api.example.com/users";
    
    // Constructor
    public UserData(String firstName, String lastName, String email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = email;
    }
    
    // Getters and setters
    public String getFirstName() {
        return firstName;
    }
    
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }
    
    public String getLastName() {
        return lastName;
    }
    
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    
    public String getEmailAddress() {
        return emailAddress;
    }
    
    public void setEmailAddress(String emailAddress) {
        // Validate email format
        if (emailAddress != null && emailAddress.contains("@")) {
            this.emailAddress = emailAddress;
        } else {
            throw new IllegalArgumentException("Invalid email format");
        }
    }
    
    public String getPhoneNumber() {
        return phoneNumber;
    }
    
    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }
    
    public String getSocialSecurityNumber() {
        return socialSecurityNumber;
    }
    
    public void setSocialSecurityNumber(String ssn) {
        // Mask SSN for security
        if (ssn != null && ssn.length() == 11) {
            this.socialSecurityNumber = "***-**-" + ssn.substring(7);
        } else {
            this.socialSecurityNumber = ssn;
        }
    }
    
    public String getDateOfBirth() {
        return dateOfBirth;
    }
    
    public void setDateOfBirth(String dateOfBirth) {
        this.dateOfBirth = dateOfBirth;
    }
    
    public String getHomeAddress() {
        return homeAddress;
    }
    
    public void setHomeAddress(String homeAddress) {
        this.homeAddress = homeAddress;
    }
    
    public String getZipCode() {
        return zipCode;
    }
    
    public void setZipCode(String zipCode) {
        this.zipCode = zipCode;
    }
    
    // Business logic methods
    public String getFullName() {
        return firstName + " " + lastName;
    }
    
    public boolean isValidEmail() {
        return emailAddress != null && emailAddress.contains("@") && emailAddress.contains(".");
    }
    
    public void updateUserInfo(String newEmail, String newPhone) {
        // Update user information
        if (newEmail != null) {
            setEmailAddress(newEmail);
        }
        if (newPhone != null) {
            setPhoneNumber(newPhone);
        }
        
        // Log the update
        System.out.println("User information updated at " + LocalDateTime.now());
    }
    
    // Data export method
    public String exportToCSV() {
        StringBuilder csv = new StringBuilder();
        csv.append("First Name,Last Name,Email,Phone,SSN,DOB,Address,ZIP\n");
        csv.append(firstName).append(",");
        csv.append(lastName).append(",");
        csv.append(emailAddress).append(",");
        csv.append(phoneNumber).append(",");
        csv.append(socialSecurityNumber).append(",");
        csv.append(dateOfBirth).append(",");
        csv.append(homeAddress).append(",");
        csv.append(zipCode).append("\n");
        return csv.toString();
    }
    
    // Main method for testing
    public static void main(String[] args) {
        // Create a test user
        UserData user = new UserData("John", "Doe", "john.doe@example.com");
        user.setPhoneNumber("555-123-4567");
        user.setSocialSecurityNumber("123-45-6789");
        user.setDateOfBirth("1980-01-15");
        user.setHomeAddress("123 Main Street");
        user.setZipCode("12345");
        
        // Display user information
        System.out.println("User: " + user.getFullName());
        System.out.println("Email: " + user.getEmailAddress());
        System.out.println("Phone: " + user.getPhoneNumber());
        System.out.println("SSN: " + user.getSocialSecurityNumber());
        
        // Export data
        System.out.println("\nCSV Export:");
        System.out.println(user.exportToCSV());
    }
}
