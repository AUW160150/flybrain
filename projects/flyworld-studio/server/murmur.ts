/**
 * @license
 * Copyright 2016 Google Inc.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Vendored from google/neuroglancer src/util/hash.ts; specialized 64-bit input.
function murmurHash3_x86_128Mix(h: number) {
  h ^= h >>> 16;
  h = Math.imul(h, 0x85ebca6b);
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35);
  h ^= h >>> 16;
  return h;
}

function rotl32(x: number, r: number) {
  return (x << r) | (x >>> (32 - r));
}

/**
 * MurmurHash3_x86_128, specialized for 8 bytes of input.
 *
 * Only the low 8 bytes of output are returned.
 */
export function murmurHash3_x86_128Hash64Bits_Bigint(
  seed: number,
  input: bigint,
): bigint {
  let h1 = seed;
  let h2 = seed;
  let h3 = seed;
  let h4 = seed;
  const c1 = 0x239b961b;
  const c2 = 0xab0e9789;
  const c3 = 0x38b34ae5;
  // const c4 = 0xa1e38b93;

  let k2 = Math.imul(Number(input >> BigInt(32)), c2);
  k2 = rotl32(k2, 16);
  k2 = Math.imul(k2, c3);
  h2 ^= k2;

  let k1 = Math.imul(Number(input & BigInt(0xffffffff)), c1);
  k1 = rotl32(k1, 15);
  k1 = Math.imul(k1, c2);
  h1 ^= k1;

  const len = 8;

  h1 ^= len;
  h2 ^= len;
  h3 ^= len;
  h4 ^= len;

  h1 = (h1 + h2) >>> 0;
  h1 = (h1 + h3) >>> 0;
  h1 = (h1 + h4) >>> 0;
  h2 = (h2 + h1) >>> 0;
  h3 = (h3 + h1) >>> 0;
  h4 = (h4 + h1) >>> 0;

  h1 = murmurHash3_x86_128Mix(h1);
  h2 = murmurHash3_x86_128Mix(h2);
  h3 = murmurHash3_x86_128Mix(h3);
  h4 = murmurHash3_x86_128Mix(h4);

  h1 = (h1 + h2) >>> 0;
  h1 = (h1 + h3) >>> 0;
  h1 = (h1 + h4) >>> 0;
  h2 = (h2 + h1) >>> 0;

  // h3 = (h3 + h1) >>> 0;
  // h4 = (h4 + h1) >>> 0;

  return BigInt(h1) | (BigInt(h2) << BigInt(32));
}
