import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

export const appDesignTokens = {
  colorBgBase: '#081116',
  colorBgContainer: '#101b22',
  colorBgElevated: '#14222b',
  colorBorder: '#263843',
  colorBorderSecondary: '#2f4652',
  colorPrimary: '#22c7b8',
  colorText: '#edf7f6',
  colorTextSecondary: '#9fb4bb',
  colorTextTertiary: '#8da4ad',
  shadowSecondary: '0 24px 80px rgba(0, 0, 0, 0.34)',
} as const;

export function applyAppDesignTokens() {
  const root = document.documentElement;

  Object.entries(appDesignTokens).forEach(([key, value]) => {
    const variableName = key.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
    root.style.setProperty(`--app-${variableName}`, value);
  });
}

export const appTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorBgBase: appDesignTokens.colorBgBase,
    colorBgContainer: appDesignTokens.colorBgContainer,
    colorBgElevated: appDesignTokens.colorBgElevated,
    colorBorder: appDesignTokens.colorBorder,
    colorBorderSecondary: appDesignTokens.colorBorderSecondary,
    colorPrimary: appDesignTokens.colorPrimary,
    colorText: appDesignTokens.colorText,
    colorTextSecondary: appDesignTokens.colorTextSecondary,
    borderRadius: 8,
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
};
