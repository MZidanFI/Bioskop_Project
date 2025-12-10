import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '30s', target: 20 },
    { duration: '5s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};

export default function () {
  const res = http.get('http://127.0.0.1:5000/');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'app is running': (r) => r.body.includes('CINEMA X1X'),
  });
  
  sleep(1);
}