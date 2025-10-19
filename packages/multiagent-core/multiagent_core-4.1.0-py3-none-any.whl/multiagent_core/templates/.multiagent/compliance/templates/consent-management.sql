-- Consent Management Database Schema
-- Purpose: Track user consent for GDPR/CCPA compliance
-- Implements: Granular consent tracking, audit trail, withdrawal mechanism

-- Consent purposes table
CREATE TABLE consent_purposes (
    id SERIAL PRIMARY KEY,
    purpose_code VARCHAR(50) UNIQUE NOT NULL,
    purpose_name VARCHAR(255) NOT NULL,
    description TEXT,
    legal_basis VARCHAR(50) NOT NULL, -- 'consent', 'contract', 'legal_obligation', 'legitimate_interest'
    is_required BOOLEAN DEFAULT FALSE,
    category VARCHAR(50), -- 'essential', 'analytics', 'marketing', 'personalization'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User consent records
CREATE TABLE user_consents (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    purpose_id INTEGER REFERENCES consent_purposes(id),
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMP DEFAULT NOW(),
    consent_source VARCHAR(100), -- 'web', 'mobile_app', 'api', 'admin'
    ip_address INET,
    user_agent TEXT,
    consent_version VARCHAR(20), -- Version of privacy policy/terms
    expires_at TIMESTAMP, -- Optional expiry date
    withdrawn_at TIMESTAMP NULL,
    withdrawal_reason TEXT,
    INDEX idx_user_id (user_id),
    INDEX idx_purpose_id (purpose_id),
    INDEX idx_consent_date (consent_date)
);

-- Consent audit log (immutable)
CREATE TABLE consent_audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    purpose_id INTEGER REFERENCES consent_purposes(id),
    action VARCHAR(50) NOT NULL, -- 'granted', 'withdrawn', 'modified'
    previous_state BOOLEAN,
    new_state BOOLEAN,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    notes TEXT,
    INDEX idx_user_audit (user_id),
    INDEX idx_timestamp (timestamp)
);

-- Insert common consent purposes
INSERT INTO consent_purposes (purpose_code, purpose_name, description, legal_basis, is_required, category) VALUES
('essential', 'Essential Services', 'Required for basic platform functionality', 'contract', TRUE, 'essential'),
('analytics', 'Analytics & Performance', 'Help us improve our service through usage analytics', 'consent', FALSE, 'analytics'),
('marketing', 'Marketing Communications', 'Receive promotional emails and offers', 'consent', FALSE, 'marketing'),
('personalization', 'Personalized Content', 'Customize your experience based on preferences', 'consent', FALSE, 'personalization'),
('third_party_sharing', 'Third-Party Data Sharing', 'Share data with trusted partners', 'consent', FALSE, 'marketing'),
('profiling', 'Automated Profiling', 'Use AI to analyze behavior and preferences', 'consent', FALSE, 'personalization');

-- Function to grant consent
CREATE OR REPLACE FUNCTION grant_consent(
    p_user_id VARCHAR,
    p_purpose_code VARCHAR,
    p_consent_source VARCHAR,
    p_ip_address INET,
    p_user_agent TEXT,
    p_consent_version VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    v_purpose_id INTEGER;
    v_consent_id INTEGER;
BEGIN
    -- Get purpose ID
    SELECT id INTO v_purpose_id FROM consent_purposes WHERE purpose_code = p_purpose_code;

    IF v_purpose_id IS NULL THEN
        RAISE EXCEPTION 'Invalid purpose code: %', p_purpose_code;
    END IF;

    -- Check if consent already exists
    SELECT id INTO v_consent_id FROM user_consents
    WHERE user_id = p_user_id AND purpose_id = v_purpose_id AND withdrawn_at IS NULL;

    IF v_consent_id IS NOT NULL THEN
        -- Update existing consent
        UPDATE user_consents
        SET consent_given = TRUE,
            consent_date = NOW(),
            consent_source = p_consent_source,
            ip_address = p_ip_address,
            user_agent = p_user_agent,
            consent_version = p_consent_version
        WHERE id = v_consent_id;
    ELSE
        -- Insert new consent
        INSERT INTO user_consents (user_id, purpose_id, consent_given, consent_source, ip_address, user_agent, consent_version)
        VALUES (p_user_id, v_purpose_id, TRUE, p_consent_source, p_ip_address, p_user_agent, p_consent_version)
        RETURNING id INTO v_consent_id;
    END IF;

    -- Log in audit trail
    INSERT INTO consent_audit_log (user_id, purpose_id, action, new_state, ip_address, user_agent)
    VALUES (p_user_id, v_purpose_id, 'granted', TRUE, p_ip_address, p_user_agent);

    RETURN v_consent_id;
END;
$$ LANGUAGE plpgsql;

-- Function to withdraw consent
CREATE OR REPLACE FUNCTION withdraw_consent(
    p_user_id VARCHAR,
    p_purpose_code VARCHAR,
    p_reason TEXT,
    p_ip_address INET
) RETURNS BOOLEAN AS $$
DECLARE
    v_purpose_id INTEGER;
    v_consent_id INTEGER;
BEGIN
    -- Get purpose ID
    SELECT id INTO v_purpose_id FROM consent_purposes WHERE purpose_code = p_purpose_code;

    IF v_purpose_id IS NULL THEN
        RAISE EXCEPTION 'Invalid purpose code: %', p_purpose_code;
    END IF;

    -- Find active consent
    SELECT id INTO v_consent_id FROM user_consents
    WHERE user_id = p_user_id AND purpose_id = v_purpose_id AND withdrawn_at IS NULL;

    IF v_consent_id IS NULL THEN
        RETURN FALSE; -- No active consent to withdraw
    END IF;

    -- Withdraw consent
    UPDATE user_consents
    SET withdrawn_at = NOW(),
        withdrawal_reason = p_reason
    WHERE id = v_consent_id;

    -- Log in audit trail
    INSERT INTO consent_audit_log (user_id, purpose_id, action, previous_state, new_state, ip_address, notes)
    VALUES (p_user_id, v_purpose_id, 'withdrawn', TRUE, FALSE, p_ip_address, p_reason);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to check if user has given consent
CREATE OR REPLACE FUNCTION has_consent(
    p_user_id VARCHAR,
    p_purpose_code VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    v_has_consent BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM user_consents uc
        JOIN consent_purposes cp ON uc.purpose_id = cp.id
        WHERE uc.user_id = p_user_id
        AND cp.purpose_code = p_purpose_code
        AND uc.consent_given = TRUE
        AND uc.withdrawn_at IS NULL
        AND (uc.expires_at IS NULL OR uc.expires_at > NOW())
    ) INTO v_has_consent;

    RETURN v_has_consent;
END;
$$ LANGUAGE plpgsql;

-- View for active consents
CREATE OR REPLACE VIEW active_consents AS
SELECT
    uc.user_id,
    cp.purpose_code,
    cp.purpose_name,
    cp.category,
    uc.consent_given,
    uc.consent_date,
    uc.consent_source,
    uc.consent_version,
    uc.expires_at
FROM user_consents uc
JOIN consent_purposes cp ON uc.purpose_id = cp.id
WHERE uc.withdrawn_at IS NULL
AND (uc.expires_at IS NULL OR uc.expires_at > NOW());

-- Query examples:

-- 1. Grant consent
-- SELECT grant_consent('user_123', 'analytics', 'web', '192.168.1.1'::INET, 'Mozilla/5.0...', '1.0');

-- 2. Withdraw consent
-- SELECT withdraw_consent('user_123', 'analytics', 'Privacy concerns', '192.168.1.1'::INET);

-- 3. Check if user has consent
-- SELECT has_consent('user_123', 'analytics');

-- 4. Get all active consents for user
-- SELECT * FROM active_consents WHERE user_id = 'user_123';

-- 5. Get consent audit trail for user
-- SELECT * FROM consent_audit_log WHERE user_id = 'user_123' ORDER BY timestamp DESC;

-- 6. Find users who withdrew specific consent
-- SELECT DISTINCT user_id FROM consent_audit_log
-- WHERE purpose_id = (SELECT id FROM consent_purposes WHERE purpose_code = 'marketing')
-- AND action = 'withdrawn'
-- AND timestamp > NOW() - INTERVAL '30 days';
