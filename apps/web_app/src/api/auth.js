import axios from 'axios';

/** POST /auth/register — Customer registration */
export async function registerCustomer(data) {
  const res = await axios.post('/auth/register', {
    username: data.username,
    email: data.email,
    password: data.password,
    full_name: data.fullName,
    is_lawyer: false,
  });
  return res.data;
}

/** POST /auth/register — Lawyer registration */
export async function registerLawyer(data) {
  const res = await axios.post('/auth/register', {
    username: data.username,
    email: data.email,
    password: data.password,
    full_name: data.fullName,
    is_lawyer: true,
    bar_registration_number: data.barNumber,
    practice_domains: data.practiceDomains,
    years_of_experience: Number(data.yearsExp),
    bio: data.bio,
  });
  return res.data;
}

/** POST /auth/lawyer/verify-documents — Upload verification file */
export async function uploadVerificationDoc(file, documentType, token) {
  const form = new FormData();
  form.append('document_type', documentType);
  form.append('file', file);
  const res = await axios.post('/auth/lawyer/verify-documents', form, {
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: `Bearer ${token}`,
    },
  });
  return res.data;
}

/** POST /auth/token — Login (form-urlencoded) */
export async function loginUser(username, password) {
  const params = new URLSearchParams();
  params.append('grant_type', 'password');
  params.append('username', username);
  params.append('password', password);
  const res = await axios.post('/auth/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return res.data; // { access_token, token_type }
}

/** GET /auth/me — Fetch current user profile */
export async function getMe() {
  const res = await axios.get('/auth/me');
  return res.data;
}
