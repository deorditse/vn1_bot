import type { ThemeConfig } from 'antd';

export const appDesignTokens = {
  colorBgBase: '#f3f5f8',
  colorBgContainer: '#ffffff',
  colorBgElevated: '#fbfcfd',
  colorBorder: '#e2e7ee',
  colorBorderSecondary: '#edf0f4',
  colorPrimary: '#e31f2b',
  colorPrimaryHover: '#c91722',
  colorAction: '#e31f2b',
  colorText: '#191b22',
  colorTextSecondary: '#596273',
  colorTextTertiary: '#8a93a3',
  shadowSecondary: '0 18px 48px rgba(27, 36, 52, 0.08)',
} as const;

export function applyAppDesignTokens() {
  const root = document.documentElement;

  Object.entries(appDesignTokens).forEach(([key, value]) => {
    const variableName = key.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
    root.style.setProperty(`--app-${variableName}`, value);
  });
}

export const appTheme: ThemeConfig = {
  token: {
    colorBgBase: appDesignTokens.colorBgBase,
    colorBgContainer: appDesignTokens.colorBgContainer,
    colorBgElevated: appDesignTokens.colorBgElevated,
    colorBorder: appDesignTokens.colorBorder,
    colorBorderSecondary: appDesignTokens.colorBorderSecondary,
    colorPrimary: appDesignTokens.colorPrimary,
    colorPrimaryHover: appDesignTokens.colorPrimaryHover,
    colorText: appDesignTokens.colorText,
    colorTextSecondary: appDesignTokens.colorTextSecondary,
    colorError: appDesignTokens.colorAction,
    borderRadius: 10,
    fontFamily:
      '"Open Sans", Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  components: {
    Button: {
      controlHeight: 42,
      borderRadius: 10,
      fontWeight: 700,
      primaryShadow: 'none',
      defaultShadow: 'none',
    },
    Input: {
      controlHeight: 42,
      borderRadius: 10,
      activeBorderColor: appDesignTokens.colorBorderSecondary,
      hoverBorderColor: appDesignTokens.colorBorderSecondary,
      activeShadow: '0 0 0 2px rgba(137, 143, 171, 0.14)',
    },
    Select: {
      activeBorderColor: appDesignTokens.colorBorderSecondary,
      activeOutlineColor: 'rgba(137, 143, 171, 0.14)',
      hoverBorderColor: appDesignTokens.colorBorderSecondary,
      optionSelectedBg: '#f1f3f6',
      optionSelectedColor: appDesignTokens.colorText,
    },
    Menu: {
      itemBorderRadius: 10,
      itemHoverBg: '#f7fafc',
      itemHoverColor: appDesignTokens.colorText,
      itemSelectedBg: '#ffffff',
      itemSelectedColor: appDesignTokens.colorText,
    },
    Progress: {
      defaultColor: appDesignTokens.colorPrimary,
      remainingColor: '#edf0f4',
    },
  },
};
