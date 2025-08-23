#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_POLICIES 10
#define MAX_CLAUSES 5

// Error levels
typedef enum {
    NO_ERROR = 0,
    LOW_WARNING = 1,
    MEDIUM_WARNING = 2,
    HIGH_WARNING = 3
} ErrorLevel;

// Clause struct: actions or constraints to enforce compliance
typedef struct {
    char description[256];
    int active; // 1 if active, 0 if inactive
} Clause;

// Policy struct: dynamic skill for system compliance
typedef struct {
    char name[64];
    char version[16]; // semver-X format
    Clause clauses[MAX_CLAUSES];
    int clause_count;
    int shuffle_enabled;      // 1 = can shuffle dynamically
    int credit_score_X;       // tracks autonomous decision trust
    ErrorLevel last_error;    // last error detected in policy execution
} Policy;

// System struct: holds all policies and monitors system state
typedef struct {
    Policy policies[MAX_POLICIES];
    int policy_count;
    ErrorLevel system_error;  // overall system error state
} DynamicScaleSystem;

// Forward declarations
void bubble_error(DynamicScaleSystem *system, int policy_index, ErrorLevel err);
int verify_policy_swap(Policy *new_policy, Policy *current_policy);
void swap_policy(DynamicScaleSystem *system, int index, Policy new_policy);
void monitor_and_update(DynamicScaleSystem *system);

// Bubble error mechanism: propagate error without breaking system
void bubble_error(DynamicScaleSystem *system, int policy_index, ErrorLevel err) {
    if (policy_index < 0 || policy_index >= system->policy_count) return;

    system->policies[policy_index].last_error = err;

    // Update system-level error if higher
    if (err > system->system_error) system->system_error = err;

    // Bubble up: notify previous policies
    for (int i = policy_index - 1; i >= 0; i--) {
        if (system->policies[i].last_error < err)
            system->policies[i].last_error = err;
    }
}

// Verify policy swap: ensure compatibility
int verify_policy_swap(Policy *new_policy, Policy *current_policy) {
    // Major version must match for safe swap
    return new_policy->version[0] == current_policy->version[0];
}

// Swap policy dynamically
void swap_policy(DynamicScaleSystem *system, int index, Policy new_policy) {
    if (index < 0 || index >= system->policy_count) return;

    if (verify_policy_swap(&new_policy, &system->policies[index])) {
        system->policies[index] = new_policy;
        printf("Policy at index %d swapped successfully.\n", index);
    } else {
        printf("Policy swap at index %d rejected due to version mismatch.\n", index);
    }
}

// Monitor and update: dynamically shuffle clauses and monitor errors
void monitor_and_update(DynamicScaleSystem *system) {
    for (int i = 0; i < system->policy_count; i++) {
        Policy *p = &system->policies[i];
        if (p->shuffle_enabled && p->clause_count > 1) {
            // Simple shuffle: swap first two clauses
            Clause temp = p->clauses[0];
            p->clauses[0] = p->clauses[1];
            p->clauses[1] = temp;
        }

        // Simulate error detection
        if (rand() % 10 < 2) { // 20% chance of low warning
            bubble_error(system, i, LOW_WARNING);
        }
    }
}

int main() {
    srand(time(NULL));
    DynamicScaleSystem system = {0};
    system.policy_count = 2;

    // Sample policy 1
    Policy p1 = {"PolicyOne", "1.0", { {"Clause A", 1}, {"Clause B", 1} }, 2, 1, 5, NO_ERROR};
    system.policies[0] = p1;

    // Sample policy 2
    Policy p2 = {"PolicyTwo", "1.0", { {"Clause X", 1}, {"Clause Y", 1} }, 2, 1, 5, NO_ERROR};
    system.policies[1] = p2;

    for (int t = 0; t < 5; t++) {
        printf("\n--- Iteration %d ---\n", t+1);
        monitor_and_update(&system);

        for (int i = 0; i < system.policy_count; i++) {
            printf("Policy: %s, Last Error: %d\n", system.policies[i].name, system.policies[i].last_error);
        }
        printf("System Error Level: %d\n", system.system_error);
    }

    // Attempt a policy swap
    Policy new_p1 = {"PolicyOneNew", "1.0", { {"Clause C", 1}, {"Clause D", 1} }, 2, 1, 5, NO_ERROR};
    swap_policy(&system, 0, new_p1);

    return 0;
}