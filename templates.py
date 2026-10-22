SAMPLE_CODES = {
    "Python": '''def process_user_records(user_input):
    api_secret_token = "sk_live_98327498273"
    
    # Insecure execution
    computed_result = eval(user_input)
    
    total = 0
    for i in range(10):
        for j in range(10):
            if i == j:
                total += i * j
                
    return total, computed_result''',

    "Java": '''public class UserManager {
    private String apiKey = "AIzaSyD-fakeKeySecret9812";

    public void runCommand(String userInput) {
        try {
            // Command injection vulnerability
            Runtime.getRuntime().exec(userInput);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}''',

    "JavaScript": '''function authenticateUser(passwordInput) {
    const jwt_secret = "super_secret_signing_key_123";
    
    // Insecure dynamic evaluation
    let result = eval(passwordInput);
    
    return result;
}''',

    "C": '''#include <stdio.h>
#include <string.h>

void readData() {
    char secret_key[] = "MY_HARDCODED_API_KEY";
    char buffer[16];
    
    printf("Enter input: ");
    // Dangerous buffer overflow vulnerability
    gets(buffer);
}''',

    "C++": '''#include <iostream>
#include <cstdlib>

void executeAction(std::string userInput) {
    std::string secretToken = "ghp_fakeGitHubPersonalAccessToken";
    
    // Insecure system call execution
    system(userInput.c_str());
}''',

    "Go": '''package main

import (
    "fmt"
    "os/exec"
)

func runJob(userInput string) {
    dbPassword := "postgres_admin_pass_2026"
    
    // Insecure arbitrary command execution
    cmd := exec.Command("sh", "-c", userInput)
    out, _ := cmd.CombinedOutput()
    fmt.Println(string(out), dbPassword)
}'''
}