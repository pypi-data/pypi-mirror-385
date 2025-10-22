# Engineering Calculation Report: Pressure Design of a Straight Pipe Under Internal Pressure

**Generated:** 2025-10-08 16:53:00

**Description:** Calculate the minimum wall thickness of a straight pipe under internal pressure according to ASME B31.3.

## 1. Known Variables

| Symbol | Name | Value | Unit |
|--------|------|-------|------|
| D | Outside Diameter | 0.84 | in |
| E | Quality Factor | 0.8 |  |
| P | Design Pressure | 90 | psi |
| S | Allowable Stress | 20000 | psi |
| T_bar | Nominal Wall Thickness | 0.147 | in |
| U_m | Mill Undertolerance | 0.125 |  |
| W | Weld Joint Strength Reduction Factor | 1 |  |
| Y | Y Coefficient | 0.4 |  |
| c | Mechanical Allowances | 0 | in |

## 2. Unknown Variables (To Calculate)

| Symbol | Name | Unit |
|--------|------|------|
| P_max | Maximum Pressure | psi |
| T | Wall Thickness | in |
| d | Inside Diameter | in |
| t | Pressure Design Thickness | in |
| t_m | Minimum Required Thickness | in |

## 3. Equations Used

1. `T = T_bar * (1  - U_m)`
2. `t = P * D / (2  * (S * E * W + P * Y))`
3. `P_max = 2  * (T - c) * S * E * W / (D - 2  * (T - c) * Y)`
4. `d = D - 2  * T`
5. `t_m = t + c`

## 4. Step-by-Step Solution

### Step 1: Solve for T

    **Equation:**
    ```
    T = T_bar * (1  - U_m)
    ```

    **Substitution:**
    ```
    T = 0.147 in * (1  - 0.125 )
    ```

    **Result:**
    ```
    T = 0.128625 in
    ```

### Step 2: Solve for t

    **Equation:**
    ```
    t = P * D / (2  * (S * E * W + P * Y))
    ```

    **Substitution:**
    ```
    t = 90 psi * 0.84 in / (2  * (20000 psi * 0.8  * 1  + 90 psi * 0.4 ))
    ```

    **Result:**
    ```
    t = 0.0023572 in
    ```

### Step 3: Solve for P_max

    **Equation:**
    ```
    P_max = 2  * (T - c) * S * E * W / (D - 2  * (T - c) * Y)
    ```

    **Substitution:**
    ```
    P_max = 2  * (0.128625 in - 0 in) * 20000 psi * 0.8  * 1  / (0.84 in - 2  * (0.128625 in - 0 in) * 0.4 )
    ```

    **Result:**
    ```
    P_max = 5584.05 psi
    ```

### Step 4: Solve for d

    **Equation:**
    ```
    d = D - 2  * T
    ```

    **Substitution:**
    ```
    d = 0.84 in - 2  * 0.128625 in
    ```

    **Result:**
    ```
    d = 0.58275 in
    ```

### Step 5: Solve for t_m

    **Equation:**
    ```
    t_m = t + c
    ```

    **Substitution:**
    ```
    t_m = 0.0023572 in + 0 in
    ```

    **Result:**
    ```
    t_m = 0.0023572 in
    ```

## 5. Summary of Results

| Variable | Name | Final Value | Unit |
|----------|------|-------------|------|
| P_max | Maximum Pressure | 5584.05 | psi |
| T | Wall Thickness | 0.128625 | in |
| d | Inside Diameter | 0.58275 | in |
| t | Pressure Design Thickness | 0.0023572 | in |
| t_m | Minimum Required Thickness | 0.0023572 | in |

---

## Disclaimer

While every effort has been made to ensure the accuracy and reliability of the calculations provided, we do not guarantee that the information is complete, up-to-date, or suitable for any specific purpose. Users must independently verify the results and assume full responsibility for any decisions or actions taken based on its output. Use of this calculator is entirely at your own risk, and we expressly disclaim any liability for errors or omissions in the information provided.

**Report Details:**
- **Generated Date:** October 08, 2025
- **Generated Using:** Qnty Library
- **Version:** Beta (Independent verification required for production use)

**Signatures:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Calculated By | _________________ | _________________ | _______ |
| Reviewed By | _________________ | _________________ | _______ |
| Approved By | _________________ | _________________ | _______ |

*Report generated using qnty library*