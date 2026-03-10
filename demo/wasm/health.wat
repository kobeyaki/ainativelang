;; Health score WASM module
;; Exports total_score(email_count, cal_count, social_count, leads_count) -> i32
;; Weights: email*2 + cal*3 + social*5 + leads*1

(module
  (func $total_score (param $email i32) (param $cal i32) (param $social i32) (param $leads i32) (result i32)
    ;; email * 2
    local.get $email
    i32.const 2
    i32.mul
    ;; + cal * 3
    local.get $cal
    i32.const 3
    i32.mul
    i32.add
    ;; + social * 5
    local.get $social
    i32.const 5
    i32.mul
    i32.add
    ;; + leads
    local.get $leads
    i32.add)
  (export "total_score" (func $total_score))
)
