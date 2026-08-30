import http from 'node:http';
import assert from 'node:assert/strict';
import { wrapFetchWithPaymentFromConfig, decodePaymentResponseHeader } from '@x402/fetch';
import { ExactEvmScheme } from '@x402/evm/exact/client';
import { generatePrivateKey, privateKeyToAccount } from 'viem/accounts';
import { getAddress, verifyTypedData } from 'viem';
import app from '../src/index.mjs';

const NETWORK = 'eip155:8453';
const CHAIN_ID = 8453;
const PAY_TO = '0x2222222222222222222222222222222222222222';
const MOCK_TX = `0x${'ab'.repeat(32)}`;

const authorizationTypes = {
  TransferWithAuthorization: [
    { name: 'from', type: 'address' },
    { name: 'to', type: 'address' },
    { name: 'value', type: 'uint256' },
    { name: 'validAfter', type: 'uint256' },
    { name: 'validBefore', type: 'uint256' },
    { name: 'nonce', type: 'bytes32' },
  ],
};

function json(res, status, body) {
  const text = JSON.stringify(body);
  res.writeHead(status, {
    'content-type': 'application/json',
    'content-length': Buffer.byteLength(text),
  });
  res.end(text);
}

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}

async function validateSignedPayment(body) {
  assert.equal(body.x402Version, 2);
  const paymentPayload = body.paymentPayload;
  const requirements = body.paymentRequirements;
  assert.equal(paymentPayload.x402Version, 2);
  assert.equal(requirements.scheme, 'exact');
  assert.equal(requirements.network, NETWORK);
  assert.equal(requirements.amount, '1000');
  assert.equal(getAddress(requirements.payTo), getAddress(PAY_TO));
  assert.equal(paymentPayload.accepted.amount, requirements.amount);
  assert.equal(paymentPayload.accepted.asset.toLowerCase(), requirements.asset.toLowerCase());

  const authorization = paymentPayload.payload.authorization;
  const signature = paymentPayload.payload.signature;
  assert.equal(getAddress(authorization.to), getAddress(PAY_TO));
  assert.equal(String(authorization.value), '1000');
  assert.ok(/^0x[0-9a-fA-F]{64}$/.test(authorization.nonce));
  assert.ok(/^0x[0-9a-fA-F]{130}$/.test(signature));

  const valid = await verifyTypedData({
    address: getAddress(authorization.from),
    domain: {
      name: requirements.extra.name,
      version: requirements.extra.version,
      chainId: CHAIN_ID,
      verifyingContract: getAddress(requirements.asset),
    },
    types: authorizationTypes,
    primaryType: 'TransferWithAuthorization',
    message: {
      from: getAddress(authorization.from),
      to: getAddress(authorization.to),
      value: BigInt(authorization.value),
      validAfter: BigInt(authorization.validAfter),
      validBefore: BigInt(authorization.validBefore),
      nonce: authorization.nonce,
    },
    signature,
  });
  assert.equal(valid, true);
  return getAddress(authorization.from);
}

let verifyCalls = 0;
let settleCalls = 0;
let verifiedPayer = null;

const facilitator = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/supported') {
      return json(res, 200, {
        kinds: [{ x402Version: 2, scheme: 'exact', network: NETWORK }],
        extensions: ['bazaar'],
        signers: { 'eip155:*': ['0x1111111111111111111111111111111111111111'] },
      });
    }

    if (req.method === 'POST' && req.url === '/verify') {
      const body = await readJson(req);
      verifiedPayer = await validateSignedPayment(body);
      verifyCalls += 1;
      return json(res, 200, { isValid: true, payer: verifiedPayer });
    }

    if (req.method === 'POST' && req.url === '/settle') {
      const body = await readJson(req);
      const payer = await validateSignedPayment(body);
      assert.equal(payer, verifiedPayer);
      settleCalls += 1;
      return json(res, 200, {
        success: true,
        payer,
        transaction: MOCK_TX,
        network: NETWORK,
        amount: '1000',
      });
    }

    return json(res, 404, { error: 'mock_not_found' });
  } catch (error) {
    return json(res, 500, { error: String(error?.message || error) });
  }
});

await new Promise((resolve, reject) => {
  facilitator.once('error', reject);
  facilitator.listen(0, '127.0.0.1', resolve);
});

try {
  const address = facilitator.address();
  assert.ok(address && typeof address === 'object');
  const facilitatorUrl = `http://127.0.0.1:${address.port}`;

  const env = {
    PAYMENTS_ENABLED: 'true',
    PAY_TO,
    NETWORK,
    FACILITATOR_URL: facilitatorUrl,
  };
  const ctx = { waitUntil() {}, passThroughOnException() {} };

  let resourceCalls = 0;
  const resourceFetch = async (input, init) => {
    resourceCalls += 1;
    const req = input instanceof Request ? new Request(input, init) : new Request(input, init);
    return app.fetch(req, env, ctx);
  };

  const account = privateKeyToAccount(generatePrivateKey());
  const paidFetch = wrapFetchWithPaymentFromConfig(resourceFetch, {
    schemes: [{ network: 'eip155:*', client: new ExactEvmScheme(account) }],
  });

  const response = await paidFetch('https://packvalue402.invalid/v1/compare', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      offers: [
        { label: '6-pack', text: '6x330 ml', price: 5.94, currency: 'USD' },
        { label: '2-liter', text: '2 L', price: 5.60, currency: 'USD' },
      ],
    }),
  });

  assert.equal(response.status, 200);
  const payload = await response.json();
  assert.equal(payload.ok, true);
  assert.equal(payload.result.winner, '2-liter');
  assert.equal(payload.target_price_usd, 0.001);
  assert.equal(verifyCalls, 1);
  assert.equal(settleCalls, 1);
  assert.equal(resourceCalls, 2);
  assert.equal(verifiedPayer, getAddress(account.address));

  const paymentResponse = response.headers.get('payment-response');
  assert.ok(paymentResponse);
  const receipt = decodePaymentResponseHeader(paymentResponse);
  assert.equal(receipt.success, true);
  assert.equal(receipt.transaction, MOCK_TX);
  assert.equal(receipt.network, NETWORK);
  assert.equal(receipt.payer, getAddress(account.address));

  console.log('X402_CRYPTOGRAPHIC_E2E_MOCK_SETTLEMENT=PASS');
  console.log(`PAYER_ADDRESS_ONLY=${account.address}`);
  console.log('PRIVATE_KEY_PERSISTED=false');
  console.log('BLOCKCHAIN_BROADCAST=false');
  console.log('REAL_VALUE_MOVED=false');
} finally {
  await new Promise(resolve => facilitator.close(resolve));
}
