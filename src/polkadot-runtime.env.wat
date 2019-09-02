(module
  (type (;0;) (func (param i32 i32 i32) (result i32)))
  (type (;1;) (func (param i32 i32) (result i32)))
  (type (;2;) (func (param i32)))
  (type (;3;) (func (param i32 i32)))
  (type (;4;) (func (param i32) (result i64)))
  (type (;5;) (func (param i32 i32 i32)))
  (type (;6;) (func (param i32 i32 i32 i32)))
  (type (;7;) (func (param i32 i32 i32 i32) (result i32)))
  (type (;8;) (func (param i32 i32 i32 i32 i32) (result i32)))
  (type (;9;) (func (param i32) (result i32)))
  (type (;10;) (func))
  (type (;11;) (func (param i64 i32) (result i32)))
  (type (;12;) (func (param i32 i32) (result i64)))
  (type (;13;) (func (param i32 i64 i64 i32 i32 i32 i32)))
  (type (;14;) (func (param i32 i32 i32 i64 i64)))
  (type (;15;) (func (param i32 i64 i64)))
  (type (;16;) (func (param i32 i64 i64 i32)))
  (type (;17;) (func (param i32 i64 i64 i64 i64)))
  (type (;18;) (func (param i32 i64 i64 i64 i64 i32)))
  (func $ext_blake2_256                      (export "ext_blake2_256"                     ) (type 5)) ;; no return
  (func $ext_twox_128                        (export "ext_twox_128"                       ) (type 5)) ;; no return
  (func $ext_get_allocated_storage           (export "ext_get_allocated_storage"          ) (type 0)) ;; return i32
  (func $ext_set_storage                     (export "ext_set_storage"                    ) (type 6)) ;; no return
  (func $ext_clear_storage                   (export "ext_clear_storage"                  ) (type 3)) ;; no return
  (func $ext_storage_root                    (export "ext_storage_root"                   ) (type 2)) ;; no return
  (func $ext_storage_changes_root            (export "ext_storage_changes_root"           ) (type 0)) ;; return i32
  (func $ext_sr25519_verify                  (export "ext_sr25519_verify"                 ) (type 7)) ;; return i32
  (func $ext_ed25519_verify                  (export "ext_ed25519_verify"                 ) (type 7)) ;; return i32
  (func $ext_get_storage_into                (export "ext_get_storage_into"               ) (type 8)) ;; return i32
  (func $ext_print_utf8                      (export "ext_print_utf8"                     ) (type 3)) ;; no return
  (func $ext_print_hex                       (export "ext_print_hex"                      ) (type 3)) ;; no return
  (func $ext_ed25519_generate                (export "ext_ed25519_generate"               ) (type 6)) ;; no return
  (func $ext_sr25519_generate                (export "ext_sr25519_generate"               ) (type 6)) ;; no return
  (func $ext_blake2_256_enumerated_trie_root (export "ext_blake2_256_enumerated_trie_root") (type 6)) ;; no return
  (func $ext_clear_prefix                    (export "ext_clear_prefix"                   ) (type 3)) ;; no return
  (func $ext_malloc                          (export "ext_malloc"                         ) (type 9)) ;; return i32
  (func $ext_free                            (export "ext_free"                           ) (type 2)) ;; no return
)

(register "env")

